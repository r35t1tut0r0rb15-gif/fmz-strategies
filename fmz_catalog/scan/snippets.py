"""Extract custom indicator code from the Pine strategies and dedupe it.

A snippet is one of:
  * a user function body (``name(args) =>`` plus its indented block),
    skipping obvious non-indicator helpers (dates, labels, sizing, alerts...);
  * a recursive series line outside functions (``x := f(x[1])`` / ``nz(x[1])``);
  * a ``for`` loop that accumulates over past bars (``src[i]``).
Snippets are normalised (comments, whitespace, ta./math. prefixes, case)
so identical code across strategies collapses into one entry.

    python fmz_catalog/scan/snippets.py code.json snippets.json
"""

import collections
import hashlib
import json
import re
import sys

SKIP_FN = re.compile(
    r"(date|time|window|period|session|label|line|box|table|plot|alert|color|colour|qty|size|lot|"
    r"position|risk|money|equity|profit|loss|stop|tp|sl|exit|enter|entry|long|short|order|trade|"
    r"debug|print|draw|fill|cell|str|text|grid|round|truncate|toint|pips|points|percent|"
    r"inrange|is_newbar|newbar|bar_?in|backtest|test|res|reso|tf|security|sec|get_?round)",
    re.I,
)


def strip_comments(code):
    return re.sub(r"//.*", "", code)


def norm(text):
    t = strip_comments(text)
    t = re.sub(r"\b(?:ta|math)\.", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def functions(lines):
    out = []
    for i, l in enumerate(lines):
        m = re.match(r"^(\w+)\s*\(([^)\n]*)\)\s*=>\s*(.*)$", l)
        if not m:
            continue
        name = m.group(1)
        body = [m.group(3)] if m.group(3).strip() else []
        for l2 in lines[i + 1:]:
            if l2.strip() == "":
                if body:
                    continue
                continue
            if not l2[:1].isspace():
                break
            body.append(l2)
        out.append((name, "\n".join(body), i))
    return out


def recursive_lines(lines):
    out = []
    for i, l in enumerate(lines):
        if l[:1].isspace():
            continue
        m = re.match(r"^\s*(?:var\s+)?(?:float\s+|int\s+)?(\w+)\s*:?=\s*(.+)$", l)
        if not m:
            continue
        v, rhs = m.group(1), m.group(2)
        if re.search(rf"\b{re.escape(v)}\s*\[\s*1\s*\]", rhs) and not re.search(r"strategy\.|label|line\.|color", rhs):
            out.append((v, l.strip(), i))
    return out


def loops(lines):
    out = []
    for i, l in enumerate(lines):
        if not re.match(r"^\s*for\s+\w+\s*=", l):
            continue
        ind = len(l) - len(l.lstrip())
        body = [l]
        for l2 in lines[i + 1:]:
            if l2.strip() and (len(l2) - len(l2.lstrip())) <= ind:
                break
            body.append(l2)
        txt = "\n".join(body)
        if re.search(r"\w+\s*\[\s*\w+\s*\]", txt) and re.search(r"\+=|:=", txt):
            out.append(("for", txt, i))
    return out


def main(code_json, out_json):
    data = json.load(open(code_json))
    snippets = {}
    per_file = collections.defaultdict(list)
    for f, code in data.get("PineScript", []):
        lines = strip_comments(code).split("\n")
        found = []
        for name, body, _ in functions(lines):
            if SKIP_FN.search(name) or len(body.strip()) < 15:
                continue
            found.append(("fn", name, body))
        for v, line, _ in recursive_lines(lines):
            found.append(("rec", v, line))
        for _, body, _ in loops(lines):
            found.append(("loop", "for", body))
        for kind, name, body in found:
            n = norm(body)
            h = hashlib.sha1(n.encode()).hexdigest()[:12]
            s = snippets.setdefault(h, {"kind": kind, "names": collections.Counter(), "code": body, "files": []})
            s["names"][name.lower()] += 1
            s["files"].append(f)
            per_file[f].append(h)
    for s in snippets.values():
        s["names"] = dict(s["names"])
        s["files"] = sorted(set(s["files"]))
    json.dump({"snippets": snippets, "per_file": per_file}, open(out_json, "w"), ensure_ascii=False)
    kinds = collections.Counter(s["kind"] for s in snippets.values())
    print("unique snippets:", len(snippets), dict(kinds))
    print("files with custom indicator code:", len(per_file))
    sizes = collections.Counter(len(s["files"]) for s in snippets.values())
    print("snippets shared by >=2 files:", sum(v for k, v in sizes.items() if k >= 2))
    print("total code chars to review:", sum(len(s["code"]) for s in snippets.values()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
