"""Cloud lane: close one batch after batch_checks.py passed. Refuses if origin/survey (the desktop lane) decided any
of the batch's ids meanwhile; then git commit, push to origin/fmz-c-cloud (verified), and the LOG entry with its
RESUME POINT in fmz_c_cloud/LOG.md (second commit, pushed). Stops at the first failure.
Usage: python3 -X utf8 -I fmz_c_cloud/finish_batch.py <batch> <summary.md>   (summary: ported / rejected, in words)"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
SP = TOOLS / "batches"
LOG = TOOLS / "LOG.md"
BRANCH = "fmz-c-cloud"
sys.path.insert(0, str(REPO / "survey_tools"))
import fmz_lanes  # noqa: E402

TRAILER = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"


def sh(args, check=True):
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise RuntimeError(f"{args}: exit {r.returncode}: {(r.stdout + r.stderr)[-1500:]}")
    return (r.stdout + r.stderr).strip()


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_log(text):
    old = LOG.read_bytes().decode("utf-8") if LOG.exists() else ""
    LOG.write_bytes((old + text).encode("utf-8"))


def push_verified():
    sh(["git", "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}"])
    commit = sh(["git", "rev-parse", "HEAD"])
    remote = sh(["git", "ls-remote", "origin", f"refs/heads/{BRANCH}"]).split()[0]
    if remote != commit:
        raise RuntimeError(f"remote {BRANCH} {remote} != local {commit}")
    return commit


def main():
    batch, summary = sys.argv[1], Path(sys.argv[2]).read_bytes().decode("utf-8").strip()
    spec = json.loads((SP / f"{batch}.json").read_bytes().decode("utf-8"))
    ported = sorted(int(i) for i in spec.get("sizing", {}))
    rejected = sorted(int(i) for i in spec.get("rejected", {}))
    dups = sorted(int(i) for i in spec.get("duplicate", {}))
    held = sorted(int(i) for i in spec.get("held", {}))
    ids = ported + rejected + dups + held
    lo, hi = min(ids), max(ids)
    if sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]) != BRANCH:
        raise SystemExit(f"refused: not on branch {BRANCH}")
    clash = sorted(set(ids) & fmz_lanes.other_lane("cloud")[0])
    if clash:
        raise SystemExit(f"refused: origin/survey (desktop lane) already decided {clash}; take these ids out of the "
                         "batch (their ports/ folders, the batch json entries, make_port_files again) and rerun")
    step = "commit"
    try:
        sh(["git", "add", "-A"])
        msg = (f"survey cloud batch {batch}: {len(ported)} ports, {len(rejected)} rejected"
               + (f", {len(dups)} duplicates" if dups else "") + (f", {len(held)} held" if held else "")
               + f" (ids {lo}-{hi})\n\nFMZ-C cloud lane (descending), rules 2026-10-15 in SURVEY_README.md."
               + TRAILER)
        (SP / "_msg_tmp.txt").write_bytes(msg.encode("utf-8"))
        sh(["git", "reset", "-q", "--", str((SP / "_msg_tmp.txt").relative_to(REPO))], check=False)
        sh(["git", "commit", "-q", "-F", str(SP / "_msg_tmp.txt")])
        step = "push"
        commit = push_verified()
    except Exception as e:  # noqa: BLE001
        append_log(f"\n## {now()} BATCH {batch} NOT FINISHED at step {step}: {e}\n"
                   f"RESUME POINT: batch {batch} files written and checked; redo finish_batch.py {batch} from "
                   f"step {step}.\n")
        raise SystemExit(f"stopped at {step}: {e}")
    q = fmz_lanes.queue("cloud")
    nxt = q["available"][0] if q["available"] else None
    append_log(f"\n## {now()} Batch {batch} (ids {lo}-{hi}): {len(ported)} ported, {len(rejected)} rejected"
               + (f", {len(dups)} duplicates" if dups else "") + (f", {len(held)} held (volume)" if held else "")
               + "\n" + summary + "\n"
               f"Checks: batch_checks.py {batch} ALL STEPS OK (py_compile, check_ports 0 problems, summarize). "
               f"Commit {commit[:7]} pushed to origin/{BRANCH} (verified equal).\n\n"
               f"RESUME POINT: batch {batch} done and pushed ({commit[:7]}). Next cloud id: {nxt} "
               f"({len(q['available'])} available to the cloud lane, {q['left_total']} undecided on both branches). "
               "Nothing half-done.\n")
    sh(["git", "add", str(LOG.relative_to(REPO))])
    (SP / "_msg_tmp.txt").write_bytes((f"fmz-c-cloud LOG: batch {batch} RESUME POINT" + TRAILER).encode("utf-8"))
    sh(["git", "commit", "-q", "-F", str(SP / "_msg_tmp.txt")])
    push_verified()
    print(f"batch {batch} finished: commit {commit[:7]}, next cloud id {nxt}, {len(q['available'])} available")


if __name__ == "__main__":
    main()
