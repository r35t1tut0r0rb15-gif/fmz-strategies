"""Two-lane split of the FMZ-C porting queue (2026-10-21, Austin: "also get a cloud session up and running doing the
same thing"). Static, read only: it reads CSV files and git refs, never a strategy.

- Desktop lane (FMZ-C, desktop GAME_CHAMBER, branch `survey`): PORT_CANDIDATE ids ASCENDING.
- Cloud lane (FMZ-C cloud, branch `fmz-c-cloud`): PORT_CANDIDATE ids DESCENDING.

Each lane fetches the other lane's branch before every batch and
  1. skips every id the other branch has decided (review_decisions.csv), and
  2. stops before the other lane's frontier, keeping BUFFER queue ids clear of it while the other lane is ACTIVE
     (a commit on its branch less than STALE_HOURS ago and no "STATUS: done" line in its lane log), so a batch
     the other lane is working on is never taken twice. A stale or finished lane releases the buffer.
Desktop frontier seen by the cloud: the highest PORT_CANDIDATE id decided on `survey`.
Cloud frontier seen by the desktop: the lowest PORT_CANDIDATE id decided on `fmz-c-cloud` but not on `survey`.
Before committing a batch, a lane re-runs `queue()` and drops any id the other branch decided meanwhile.

Usage (from the repository root): python -X utf8 -I survey_tools/fmz_lanes.py desktop|cloud [N]
"""
import csv
import io
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUFFER = 15
STALE_HOURS = 3.0
LANES = {
    "desktop": {"branch": "survey", "order": "asc", "other": "cloud"},
    "cloud": {"branch": "fmz-c-cloud", "order": "desc", "other": "desktop"},
}
LANE_LOG = {"cloud": "fmz_c_cloud/LOG.md", "desktop": "fmz_c_cloud/DESKTOP_LANE_STATUS.md"}


def _git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def _decided(text):
    return {int(r["fmz_id"]) for r in csv.DictReader(io.StringIO(text))}


def other_lane(lane):
    """(decided ids, hours since its last commit, active) of the other lane's branch on origin."""
    other = LANES[lane]["other"]
    br = LANES[other]["branch"]
    _git("fetch", "-q", "origin", br)
    rc, out = _git("show", f"origin/{br}:review_decisions.csv")
    if rc:
        return set(), None, False                      # branch not on origin: no other lane
    rc, ct = _git("log", "-1", "--format=%ct", f"origin/{br}")
    age = (time.time() - int(ct.strip())) / 3600 if rc == 0 and ct.strip() else None
    rc, log = _git("show", f"origin/{br}:{LANE_LOG[other]}")
    done = rc == 0 and "\nSTATUS: done" in "\n" + log
    active = age is not None and age < STALE_HOURS and not done
    return _decided(out), age, active


def queue(lane):
    rows = list(csv.DictReader(open(REPO / "screening.csv", encoding="utf-8")))
    cand = {int(r["fmz_id"]) for r in rows if r["overall"] == "PORT_CANDIDATE"}
    mine = _decided((REPO / "review_decisions.csv").read_bytes().decode("utf-8"))
    other, age, active = other_lane(lane)
    left = sorted(cand - mine - other, reverse=LANES[lane]["order"] == "desc")
    if lane == "desktop":
        own = (other - mine) & cand
        frontier = min(own) if own else None
        avail = [i for i in left if frontier is None or i < frontier]
    else:
        dec = other & cand
        frontier = max(dec) if dec else None
        avail = [i for i in left if frontier is None or i > frontier]
    if active and frontier is not None:
        avail = avail[:-BUFFER] if len(avail) > BUFFER else []
    return {"lane": lane, "left_total": len(left), "available": avail, "other_frontier": frontier,
            "other_age_hours": None if age is None else round(age, 2), "other_active": active}


def main():
    lane = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    q = queue(lane)
    print(f"LANE {lane}: {q['left_total']} ids left undecided on both branches; {len(q['available'])} available "
          f"to this lane; other lane frontier {q['other_frontier']}, last commit {q['other_age_hours']} h ago, "
          f"active {q['other_active']}")
    print("NEXT", " ".join(map(str, q["available"][:n])) or "(none)")


if __name__ == "__main__":
    main()
