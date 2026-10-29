"""Combine the scans into per-strategy and per-indicator results.

Inputs (from the repo root):
  code.json            extract_sources.py output
  usage.json           detect.py output (built-in / pattern tags per strategy)
  snippets.json        snippets.py output (custom code -> strategies)
  review/result_*.jsonl  per-snippet verdicts

    python fmz_catalog/scan/aggregate.py code.json usage.json snippets.json fmz_catalog/scan/summary.json

Each strategy gets the worst verdict over its custom indicator code, plus
look-ahead from the security() scan:
  lookahead > bug > variant > warmup_only > standard (or no custom code).
"""

import collections
import glob
import json
import os
import re
import sys

RANK = {"standard": 0, "warmup_only": 1, "variant": 2, "bug": 3, "lookahead": 4}


def load_results(folder):
    res = {}
    for fn in sorted(glob.glob(os.path.join(folder, "result_*.jsonl"))):
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                res[r["id"]] = r
    return res


def security_lookahead(code):
    """security(..., lookahead_on) without a [1] offset on the expression."""
    for m in re.finditer(r"\bsecurity\s*\(([^\n]*)", code):
        args = m.group(1)
        if re.search(r"lookahead\s*=\s*(barmerge\.lookahead_on|true)", args) and not re.search(r"\[\s*1\s*\]", args):
            return True
    return False


def norm_name(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9_]+", "_", s).strip("_")
    return s


def main(code_json, usage_json, snippets_json, out_json):
    code = json.load(open(code_json))
    usage = json.load(open(usage_json))
    snip = json.load(open(snippets_json))
    review = load_results(os.path.join(os.path.dirname(out_json), "review"))
    src = {f: c for lang, rows in code.items() for f, c in rows}
    lang_of = {f: lang for lang, rows in code.items() for f, _ in rows}

    per_file = {}
    for f in src:
        worst, reasons = None, []
        for h in snip["per_file"].get(f, []):
            r = review.get(h)
            if not r or r.get("verdict") == "not_indicator":
                continue
            v = r["verdict"]
            if v not in RANK:
                continue
            if v != "standard":
                reasons.append({"id": h, "verdict": v, "indicator": r.get("indicator"), "note": r.get("note")})
            if worst is None or RANK[v] > RANK[worst]:
                worst = v
        if lang_of[f] == "PineScript" and security_lookahead(src[f]):
            reasons.append({"id": "security", "verdict": "lookahead", "indicator": "security", "note": "security(..., lookahead_on) without [1]"})
            worst = "lookahead"
        tags = usage["per_file"].get(f, {}).get("tags", [])
        per_file[f] = {"lang": lang_of[f], "worst": worst or ("standard" if (tags or snip["per_file"].get(f)) else "none"),
                       "tags": tags, "issues": reasons}

    # indicator inventory: built-in tags + reviewed custom code
    inv = collections.defaultdict(lambda: {"files": set(), "verdicts": collections.Counter(), "best": collections.Counter(), "source": set()})
    for key, u in usage["usage"].items():
        e = inv["tag:" + key]
        e["label"] = u["label"]
        e["tv"] = u["tv"]
        e["files"].update(u["files"])
        e["source"].add("pattern")
    for h, s in snip["snippets"].items():
        r = review.get(h)
        if not r or r.get("verdict") == "not_indicator":
            continue
        e = inv["rev:" + norm_name(r.get("indicator"))]
        e["files"].update(s["files"])
        e["verdicts"][r["verdict"]] += len(s["files"])
        e["best"][r.get("best", "")] += len(s["files"])
        e["source"].add("review")
    inv_out = {}
    for k, e in inv.items():
        inv_out[k] = {"label": e.get("label", k.split(":", 1)[1]), "tv": e.get("tv"), "n_files": len(e["files"]),
                      "verdicts": dict(e["verdicts"]), "best": dict(e["best"].most_common(5)), "source": sorted(e["source"])}
    json.dump({"per_file": per_file, "inventory": inv_out, "n_reviewed": len(review)}, open(out_json, "w"), ensure_ascii=False, indent=0)

    total = len(per_file)
    cnt = collections.Counter(v["worst"] for v in per_file.values())
    print("strategies:", total, "snippets reviewed:", len(review), "of", len(snip["snippets"]))
    for k in ["none", "standard", "warmup_only", "variant", "bug", "lookahead"]:
        print(f"  {k:12s} {cnt.get(k, 0):5d}  {100 * cnt.get(k, 0) / total:5.1f}%")


if __name__ == "__main__":
    main(*sys.argv[1:5])
