"""Sandbox prototype: trusted status publication and merged-release dispatch."""

# This script is executed from trusted main, never from an unmerged PR checkout.
# Commands use argv and JSON stdin; no shell interpolation.
# ruff: noqa: E402, S603, S607
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/repo_tools/src"))
from repo_tools.ci_validation import verify_profile
from repo_tools.commands.check_release_automation import eligible_pr
from repo_tools.conventional_commits import valid_subject
from repo_tools.github_api import api, items
from repo_tools.github_checks import check_ci_run, check_evidence, merged_pr, verify_commit
from repo_tools.release_changes import branch_at, managed_pr

REPO = os.environ["GITHUB_REPOSITORY"]
EVENT = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())


def require(condition: bool) -> None:
    if not condition:
        raise ValueError("Release bridge validation failed")


def post(path: str, data: dict) -> dict | None:
    result = subprocess.run(
        [
            "gh",
            "api",
            "-H",
            "X-GitHub-Api-Version: 2026-03-10",
            "--method",
            "POST",
            f"repos/{REPO}/{path}",
            "--input",
            "-",
        ],
        input=json.dumps(data),
        text=True,
        check=True,
        capture_output=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


def current_pr(number: int) -> dict:
    return api(f"repos/{REPO}/pulls/{number}")


def publish(trigger: dict | None = None) -> None:
    if trigger is None:
        trigger = EVENT["workflow_run"]
    if trigger["event"] != "workflow_dispatch":
        return
    branch = branch_at(ROOT, "HEAD")
    if trigger["head_branch"] != branch:
        return
    candidates = items(
        f"repos/{REPO}/pulls?"
        + urlencode(
            {
                "state": "open",
                "base": "main",
                "head": f"{REPO.split('/')[0]}:{branch}",
                "per_page": 100,
            }
        )
    )
    matches = [p for p in candidates if p["head"]["sha"] == trigger["head_sha"]]
    if len(matches) != 1:
        print("Ignoring superseded or closed release PR validation")
        return
    pr = current_pr(matches[0]["number"])
    head = pr["head"]["sha"]
    eligible_pr(REPO, pr["number"], branch, head, root=ROOT)
    filename = Path(trigger["path"]).name
    require(filename in {"ci.yml", "pr-title.yml"})
    workflow = api(f"repos/{REPO}/actions/workflows/{filename}")
    require(trigger["workflow_id"] == workflow["id"])
    query = urlencode({"head_sha": head, "event": "workflow_dispatch", "per_page": 100})
    endpoint = f"repos/{REPO}/actions/workflows/{workflow['id']}/runs?{query}"
    latest = max(items(endpoint, "workflow_runs"), key=lambda r: r["id"])
    run = api(f"repos/{REPO}/actions/runs/{trigger['id']}")
    if latest["id"] != run["id"] or run["run_attempt"] != trigger["run_attempt"]:
        print("Ignoring superseded run or attempt")
        return
    require(all(run[k]["full_name"] == REPO for k in ("repository", "head_repository")))
    context = "CI result" if filename == "ci.yml" else "Conventional PR title"
    post(
        f"statuses/{head}",
        {
            "context": context,
            "state": "pending",
            "target_url": run["html_url"],
            "description": "Verifying latest validation attempt",
        },
    )
    state = "failure" if run["status"] == "completed" else "pending"
    if run["status"] == "completed" and run["conclusion"] == "success":
        if filename == "ci.yml":
            check_ci_run(run, REPO, pr, workflow["id"])
            evidence = check_evidence(REPO, run["id"], head, head, exact_checkout=True, root=ROOT)
            require(evidence["schema"] == 2 and evidence["base_sha"] == pr["base"]["sha"])
            verify_profile(REPO, run, evidence, head, ROOT)
        else:
            jobs = items(
                f"repos/{REPO}/actions/runs/{run['id']}/jobs?filter=latest&per_page=100", "jobs"
            )
            require(
                len(jobs) == 1 and jobs[0]["name"] == context and jobs[0]["conclusion"] == "success"
            )
            require(valid_subject(pr["title"]))
        state = "success"
    again = current_pr(pr["number"])
    if (
        again["state"] != "open"
        or again["head"]["sha"] != head
        or again["base"]["sha"] != pr["base"]["sha"]
    ):
        print("Ignoring validation after PR changed")
        return
    latest = max(items(endpoint, "workflow_runs"), key=lambda r: r["id"])
    current = api(f"repos/{REPO}/actions/runs/{run['id']}")
    if (
        latest["id"] != run["id"]
        or current["run_attempt"] != run["run_attempt"]
        or current["status"] != run["status"]
        or current["conclusion"] != run["conclusion"]
    ):
        return
    post(
        f"statuses/{head}",
        {
            "context": context,
            "state": state,
            "target_url": run["html_url"],
            "description": f"Verified run {run['id']}, attempt {run['run_attempt']}",
        },
    )
    print(f"Published {state}: {context} for PR #{pr['number']} at {head}")


def dispatch() -> str | None:
    pr = EVENT["pull_request"]
    if not pr["merged"] or pr["base"]["ref"] != "main":
        return
    if any((pr[side]["repo"] or {}).get("full_name") != REPO for side in ("base", "head")):
        return
    if pr["head"]["ref"] != branch_at(ROOT, "HEAD") or "[skip ci]" not in pr["title"]:
        return
    live = current_pr(pr["number"])
    require(live["merged"] and live["merge_commit_sha"] == pr["merge_commit_sha"])
    head = live["merge_commit_sha"]
    if api(f"repos/{REPO}/branches/main")["commit"]["sha"] != head:
        print("Ignoring obsolete merge event")
        return
    post(
        "dispatches",
        {"event_type": "lab-merged-release", "client_payload": {"pr": pr["number"], "head": head}},
    )
    print(f"Dispatched merged release verification for PR #{pr['number']} at {head}")
    return head


def verify() -> None:
    payload = EVENT["client_payload"]
    head = os.environ["GITHUB_SHA"]
    require(os.environ["GITHUB_EVENT_NAME"] == "repository_dispatch")
    require(os.environ["GITHUB_REF"] == "refs/heads/main" and payload["head"] == head)
    require(api(f"repos/{REPO}/branches/main")["commit"]["sha"] == head)
    pr, _ = merged_pr(REPO, head, root=ROOT)
    require(pr["number"] == payload["pr"])
    require(pr["head"]["ref"] == branch_at(ROOT, "HEAD"))
    workflow = api(f"repos/{REPO}/actions/workflows/ci.yml")
    commits = verify_commit(REPO, head, workflow["id"], root=ROOT)
    require(bool(commits) and commits[-1] == head)
    print(f"Verified merged release PR #{pr['number']}: {len(commits)} commit(s)")


def await_head(number: int, branch: str, head: str) -> None:
    """Wait for GitHub's PR view to catch up with the just-pushed release branch."""
    deadline = time.monotonic() + 60
    while True:
        pr = current_pr(number)
        require(pr["state"] == "open" and managed_pr(pr, REPO, branch))
        if pr["head"]["sha"] == head:
            return
        require(time.monotonic() < deadline)
        print(f"Waiting for PR #{number} head {pr['head']['sha']} to reach {head}", flush=True)
        time.sleep(2)


def coordinate() -> None:
    """Explicitly await token-dispatched runs; their workflow_run callbacks are suppressed."""
    number = int(os.environ["RELEASE_PR_NUMBER"])
    head = os.environ["RELEASE_HEAD"]
    branch = os.environ["RELEASE_BRANCH"]
    await_head(number, branch, head)
    eligible_pr(REPO, number, branch, head, root=ROOT)
    runs = []
    for filename, context, inputs in (
        ("ci.yml", "CI result", {"release-pr-number": str(number), "expected-head": head}),
        ("pr-title.yml", "Conventional PR title", {"pr-number": str(number)}),
    ):
        post(
            f"statuses/{head}",
            {
                "context": context,
                "state": "pending",
                "description": "Awaiting authoritative validation",
            },
        )
        details = post(
            f"actions/workflows/{filename}/dispatches", {"ref": branch, "inputs": inputs}
        )
        require(details is not None and isinstance(details.get("workflow_run_id"), int))
        if details is None:
            raise ValueError("Dispatch did not return a run ID")
        runs.append(details["workflow_run_id"])
        print(f"Dispatched {filename}: {details['html_url']}", flush=True)
    deadline = time.monotonic() + 35 * 60
    remaining = set(runs)
    while remaining and time.monotonic() < deadline:
        pr = current_pr(number)
        require(pr["state"] == "open" and pr["head"]["sha"] == head)
        for run_id in sorted(remaining):
            run = api(f"repos/{REPO}/actions/runs/{run_id}")
            require(run["head_sha"] == head and run["head_branch"] == branch)
            if run["status"] == "completed":
                publish(run)
                require(run["conclusion"] == "success")
                remaining.remove(run_id)
                print(f"Verified completed run {run_id}", flush=True)
        if remaining:
            time.sleep(10)
    require(not remaining)


def route() -> None:
    """Start merged verification, then explicitly start Release after it succeeds."""
    merged_head = EVENT["pull_request"]["merge_commit_sha"]
    query = urlencode(
        {"branch": "main", "event": "repository_dispatch", "head_sha": merged_head, "per_page": 100}
    )
    endpoint = f"repos/{REPO}/actions/workflows/ci.yml/runs?{query}"
    before = max((run["id"] for run in items(endpoint, "workflow_runs")), default=0)
    head = dispatch()
    if head is None:
        return
    deadline = time.monotonic() + 7 * 60
    while time.monotonic() < deadline:
        require(api(f"repos/{REPO}/branches/main")["commit"]["sha"] == head)
        candidates = [run for run in items(endpoint, "workflow_runs") if run["id"] > before]
        if candidates:
            run = max(candidates, key=lambda value: value["id"])
            if run["status"] == "completed":
                require(run["conclusion"] == "success")
                jobs = items(
                    f"repos/{REPO}/actions/runs/{run['id']}/jobs?filter=latest&per_page=100", "jobs"
                )
                verified = [job for job in jobs if job["name"] == "Merged PR verification"]
                require(len(verified) == 1 and verified[0]["conclusion"] == "success")
                details = post("actions/workflows/release.yml/dispatches", {"ref": "main"})
                print(f"Explicitly dispatched Release after CI {run['id']}: {details}")
                return
        time.sleep(10)
    raise ValueError("Timed out waiting for merged release verification")


if __name__ == "__main__":
    {
        "publish": publish,
        "dispatch": dispatch,
        "verify": verify,
        "coordinate": coordinate,
        "route": route,
    }[sys.argv[1]]()
