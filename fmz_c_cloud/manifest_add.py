"""Add one batch's entries to repo\\survey_tools\\port_manifest.py (SIZING, REJECTED_ON_READING, DUPLICATE_ON_READING).

Usage: python -X utf8 -I manifest_add.py <batch.json>
batch.json: {"batch": "C1", "date": "2026-10-15",
             "sizing": {"<id>": [["label", first, last], ...]},
             "rejected": {"<id>": ["<criterion>", "<reason>"]},
             "duplicate": {"<id>": [<ported id>, "<reason>"]}}
Patches by exact anchors, keeps LF line endings, refuses an id already present, and parses the result.
"""
import ast
import json
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "survey_tools" / "port_manifest.py"
A_SIZING = "}\n\nREJECTED_ON_READING = {"
A_REJ = "}\n\nDUPLICATE_ON_READING = {"


def wrap(text, indent, width=100):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width - indent - 4 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    lines.append(cur)
    return lines
sys.path.insert(0, str(Path(__file__).resolve().parent))
import heartbeat  # noqa: E402



def main():
    heartbeat.beat(Path(__file__).name)
    b = json.loads(Path(sys.argv[1]).read_bytes().decode("utf-8"))
    t = MANIFEST.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    tree = ast.parse(t)
    present = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            present |= {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    ids = [int(i) for part in ("sizing", "rejected", "duplicate", "held") for i in b.get(part, {})]
    dup = sorted(set(ids) & present)
    if dup or len(ids) != len(set(ids)):
        raise SystemExit(f"refused: ids already in the manifest or repeated: {dup}")
    head = f"    # ---- FMZ-C, batch {b['batch']} ({b['date']})\n"
    s = head
    for fid, blocks in sorted(b.get("sizing", {}).items(), key=lambda kv: int(kv[0])):
        if not blocks:
            s += f"    {fid}: [],\n"
            continue
        s += f"    {fid}: [\n"
        for label, a, z in blocks:
            s += f"        ({json.dumps(label, ensure_ascii=False)}, {int(a)}, {int(z)}),\n"
        s += "    ],\n"
    r = head
    for fid, (crit, why) in sorted(b.get("rejected", {}).items(), key=lambda kv: int(kv[0])):
        lines = wrap(why, 14)
        r += f"    {fid}: (\"{crit}\", " + "\n".join(
            (json.dumps(x + (" " if k < len(lines) - 1 else ""), ensure_ascii=False) if k == 0 else
             "              " + json.dumps(x + (" " if k < len(lines) - 1 else ""), ensure_ascii=False))
            for k, x in enumerate(lines)) + "),\n"
    d = head
    for fid, (rep, why) in sorted(b.get("duplicate", {}).items(), key=lambda kv: int(kv[0])):
        d += f"    {fid}: ({int(rep)}, {json.dumps(why, ensure_ascii=False)}),\n"
    for anchor in (A_SIZING, A_REJ):
        if t.count(anchor) != 1:
            raise SystemExit(f"anchor not unique: {anchor!r}")
    if b.get("sizing"):
        t = t.replace(A_SIZING, s + A_SIZING)
    if b.get("rejected"):
        t = t.replace(A_REJ, r + A_REJ)
    if b.get("duplicate"):
        i = t.rindex("}\n")
        t = t[:i] + d + t[i:]
    if b.get("held"):
        h = head
        for fid, (crit, why) in sorted(b["held"].items(), key=lambda kv: int(kv[0])):
            h += f"    {fid}: ({json.dumps(crit)}, {json.dumps(why, ensure_ascii=False)}),\n"
        k = t.index("HELD_ON_READING = {\n") + len("HELD_ON_READING = {\n")
        e = t.index("\n}", k - 1) + 1
        t = t[:e] + h + t[e:]
    ast.parse(t)
    MANIFEST.write_bytes(t.encode("utf-8"))
    print("added", len(b.get("sizing", {})), "ports,", len(b.get("rejected", {})), "rejected,",
          len(b.get("duplicate", {})), "duplicates,", len(b.get("held", {})), "held")


if __name__ == "__main__":
    main()
