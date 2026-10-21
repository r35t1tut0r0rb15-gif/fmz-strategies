"""Write one port (ports/<slug>/module.py + PORT_NOTES.md) from a compact spec file, filling the source facts
(name, author, language + Pine version, FMZ last modified, URL), the near-duplicate group and the trial count
(product of GRID) from the repo itself, so they cannot be mistyped. Added 2026-10-16 by the resumed FMZ-C session;
the output has the same shape as the hand-written C1-C18 ports. Never runs a strategy (the code is only parsed).

Usage: python -X utf8 -I write_port.py <batch> <spec.txt> [<spec.txt> ...]

Spec: sections opened by a line "@@key" (or "@@key value" for one-liners):
  id, alias (optional: the script's own title), summary, orig_lines ("a-b"), orig_head (text after the line
  reference), orig (indented signal lines), interp ("* ..." bullets), c1 / c2 ("OUTCOME | note"), c3 (note or
  "-"), c4 (note), side ("REVERSAL INTENDED." / "Long only." / "Opposite entries cannot occur." ...), marks,
  name, family, grid_note, ambig (bullets for PORT_NOTES), code (everything after the docstring).
"""
import ast
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import heartbeat  # noqa: E402

REPO = Path(__file__).resolve().parents[1]  # repository root (cloud copy, 2026-10-21)
MARKS = {"none", "bar_size_pending", "trailing_stop_pending", "trailing_stop", "coarse_bar_stop",
         "stop_is_entry_condition"}


def parse(path):
    sec, key = {}, None
    for line in path.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n"):
        m = re.match(r"^@@(\w+)(?: (.*))?$", line)
        if m:
            key = m.group(1)
            sec[key] = [m.group(2)] if m.group(2) is not None else []
        elif key is not None:
            sec[key].append(line)
    return {k: "\n".join(v).strip("\n") for k, v in sec.items()}


def eng(name):
    """The English part of a corpus name ("中文English-Words" -> "English Words"), as the C1-C18 ports."""
    m = re.search(r"[A-Za-z0-9].*$", name)
    t = m.group(0) if m else name
    return t.replace("-", " ").strip() if not re.search(r"[^\x00-\x7f]", t) else name


def cap(s):
    return s[:1].upper() + s[1:]


def main():
    heartbeat.beat(Path(__file__).name)
    batch = sys.argv[1]
    rows = {r["fmz_id"]: r for r in csv.DictReader(open(REPO / "screening.csv", encoding="utf-8"))}
    groups = {}
    for g in csv.DictReader(open(REPO / "near_duplicate_groups.csv", encoding="utf-8")):
        groups.setdefault(g["fmz_id"], []).append(g)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for sp in sys.argv[2:]:
        s = parse(Path(sp))
        fid = s["id"].strip()
        r = rows[fid]
        src = (REPO / r["file"]).read_bytes().decode("utf-8")
        if r["lang"] == "PineScript":
            v = re.search(r"@version\s*=\s*(\d)", src)
            lang = f"PineScript v{v.group(1)}" if v else "PineScript, no @version line"
        else:
            lang = r["lang"]
        code = s["code"].strip("\n") + "\n"
        tree = ast.parse(code)
        grid = next(ast.literal_eval(nd.value) for nd in tree.body if isinstance(nd, ast.Assign)
                    and any(getattr(t, "id", "") == "GRID" for t in nd.targets))
        ntr = 1
        for val in grid.values():
            ntr *= len(val)
        name = next(ast.literal_eval(nd.value) for nd in tree.body if isinstance(nd, ast.Assign)
                    and any(getattr(t, "id", "") == "NAME" for t in nd.targets))
        if name != s["name"].strip() or not name.startswith(f"fmz_{fid}_"):
            raise SystemExit(f"{fid}: NAME {name!r} vs spec {s['name']!r}")
        marks = s["marks"].strip()
        if not set(m.strip() for m in marks.split(",")) <= MARKS:
            raise SystemExit(f"{fid}: unknown mark in {marks!r}")
        gs = groups.get(fid, [])
        if gs:
            g6 = "; ".join(f"{g['group_id']} ({g['n_members']} members, best partner #{g['best_partner_id']}, "
                           f"Jaccard {g['best_jaccard']})" for g in gs)
            g6n = ", ".join(g["group_id"] for g in gs) + "."
        else:
            g6, g6n = "no DG / ND group", "No `DG` or `ND` group."
        c1o, c1n = [x.strip() for x in s["c1"].split("|", 1)]
        c2o, c2n = [x.strip() for x in s["c2"].split("|", 1)]
        c3 = s["c3"].strip()
        c4 = s["c4"].strip().rstrip(".")
        alias = f' ({s["alias"].strip()})' if s.get("alias", "").strip() else ""
        ind = lambda t: "\n".join(("    " + x) if x.strip() else "" for x in t.split("\n"))  # noqa: E731
        doc = (f'"""{s["summary"].strip()}\n'
               f'Port of FMZ strategy #{fid} "{eng(r["name"])}"{alias}.\n\n'
               f"FMZ source id: {fid}\n\n"
               "Source\n"
               f"    https://www.fmz.com/strategy/{fid} ({lang}, FMZ last modified {r['last_modified']}).\n"
               f"    Verbatim copy: original_source.md. Read {date} (FMZ-C cloud).\n\n"
               f"Original signal (original_source.md lines {s['orig_lines'].strip()}), {s['orig_head'].strip()}\n"
               f"{ind(s['orig'].strip(chr(10)))}\n\n"
               "Interpretation choices (Pine rules in SURVEY_README.md)\n"
               f"{ind(s['interp'].strip())}\n\n"
               "Admission criteria\n"
               f"    1 fits the interface: {c1o}, {c1n.rstrip('.')}.\n"
               f"    2 generic: {c2o}, {c2n.rstrip('.')}.\n"
               f"    3 crypto-exchange-only: no{'' if c3 in ('', '-') else f' ({c3})'}.\n"
               f"    4 signals only: {c4}.\n"
               f"    5 ranges declared: GRID below ({ntr} trial{'s' if ntr != 1 else ''}), before any backtest.\n"
               f"    6 near-duplicates: {g6}; ported (rule 7).\n"
               "    7 FMZ performance claims: ignored.\n"
               "Volume: not used (check 8).\n"
               f"Session open: {s.get('session', 'not used').strip() or 'not used'}.\n"
               f"{s['side'].strip()}\n\n"
               f"Marks: {marks}\n"
               '"""\n')
        if r["lang"] != "PineScript":
            doc = doc.replace("Interpretation choices (Pine rules in SURVEY_README.md)",
                              "Interpretation choices (rules in SURVEY_README.md)")
        mod = doc + code
        ast.parse(mod)
        if "KNOWN_ANSWER" in mod:
            raise SystemExit(f"{fid}: forbidden name")
        author = r["author"]
        notes = (f"# #{fid} {eng(r['name'])} -> `{name}`\n\n"
                 f"- FMZ source id: {fid} (lineage).\n"
                 f"- Source: https://www.fmz.com/strategy/{fid} ({lang}, author {author}, FMZ last\n"
                 f"  modified {r['last_modified']}). Verbatim here as `original_source.md`. Read {date} (FMZ-C cloud).\n"
                 f"- Status: PORTED (batch {batch}). Not run.\n\n"
                 "## Criteria\n\n"
                 "| # | Outcome | Notes |\n|---|---|---|\n"
                 f"| 1 | {c1o} | {cap(c1n)} |\n"
                 f"| 2 | {c2o} | {cap(c2n)} |\n"
                 f"| 3 | PASS | {'' if c3 in ('', '-') else cap(c3).rstrip('.') + '.'} |\n"
                 f"| 4 | DONE | {cap(c4)}. |\n"
                 "| 5 | DECLARED | See grid. |\n"
                 f"| 6 | PORTED (rule 7) | {g6n} |\n"
                 "| 7 | IGNORED |  |\n\n"
                 "## Declared grid (criterion 5)\n\n"
                 f"{s['grid_note'].strip().replace('@N', f'**{ntr} trial' + ('s' if ntr != 1 else '') + '**')}\n\n"
                 "## Ambiguities resolved\n\n"
                 f"{s['ambig'].strip()}\n\n"
                 "## FAMILY (proposed, user to confirm)\n\n"
                 f"`FAMILY = \"{s['family'].strip()}\"`.\n\n"
                 "## Marks\n\n"
                 f"`{marks}`\n")
        if f"**{ntr} trial" not in notes:
            raise SystemExit(f"{fid}: grid_note must contain @N")
        if f'FAMILY = "{s["family"].strip()}"' not in code:
            raise SystemExit(f"{fid}: FAMILY in code differs from the spec")
        d = REPO / "ports" / r["slug"]
        d.mkdir(exist_ok=True)
        (d / "module.py").write_bytes(mod.encode("utf-8"))
        (d / "PORT_NOTES.md").write_bytes(notes.encode("utf-8"))
        print(f"{fid}: {name}, {ntr} trials, marks {marks}")


if __name__ == "__main__":
    main()
