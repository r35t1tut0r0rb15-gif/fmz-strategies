"""Cloud lane: list the next N ids available to the cloud lane (PORT_CANDIDATE, DESCENDING, not decided on this
branch or on origin/survey, clear of the desktop lane's frontier; survey_tools/fmz_lanes.py) with file, language,
size, near-duplicate groups and slug. Read only. Usage: python3 -X utf8 -I fmz_c_cloud/next_batch.py [N]"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "survey_tools"))
import fmz_lanes  # noqa: E402


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 13
    q = fmz_lanes.queue("cloud")
    print(f"LANE cloud: {q['left_total']} ids undecided on both branches; {len(q['available'])} available to the "
          f"cloud lane; desktop frontier {q['other_frontier']}, last desktop commit {q['other_age_hours']} h ago, "
          f"desktop active {q['other_active']}")
    if not q["available"]:
        print("NOTHING AVAILABLE TO THE CLOUD LANE: see CLOUD_BRIEF.md section 5 (lane meeting).")
        return
    rows = {r["fmz_id"]: r for r in csv.DictReader(open(REPO / "screening.csv", encoding="utf-8"))}
    groups = {}
    for g in csv.DictReader(open(REPO / "near_duplicate_groups.csv", encoding="utf-8")):
        groups.setdefault(g["fmz_id"], []).append(f"{g['group_id']}({g['n_members']},{g['best_partner_id']},"
                                                   f"{g['best_jaccard']},exact={g['exact_duplicate_of']})")
    for i in q["available"][:n]:
        r = rows[str(i)]
        nlines = (REPO / r["file"]).read_bytes().count(b"\n")
        print(r["fmz_id"], r["lang"], nlines, r["slug"], ";".join(groups.get(r["fmz_id"], [])) or "-",
              "|", r["c1"], r["c2"], r["c3"], "|", r["file"])


if __name__ == "__main__":
    main()
