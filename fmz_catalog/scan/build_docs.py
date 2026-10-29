"""Build CATALOG.md, IMPACT.md and impact_by_strategy.csv from the scan outputs.

    python fmz_catalog/scan/build_docs.py usage.json summary.json

Reads fmz_catalog/scan/impl/*_report.json and impl/hpotter_files.jsonl when
present, plus the EXTRA* registries of the staging modules.
"""

import collections
import csv
import glob
import importlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RANK = {"none": -1, "standard": 0, "warmup_only": 1, "variant": 2, "bug": 3, "lookahead": 4}
MODULES = ["extra", "extra_tv", "extra_ehlers", "extra_hpotter", "extra_ma", "extra_trend", "extra_misc"]

# Severity of the strategy-copy issues the implementation agents reported,
# keyed by (family, indicator, issue index). Anything not listed is a bug.
SEVERITY = {
    **{("ehlers", "ehlers_bandpass", i): "warmup_only" for i in range(5)},     # pi = 3.14 / 3.1415
    ("ehlers", "ehlers_emd", 0): "warmup_only", ("ehlers", "ehlers_emd", 1): "warmup_only",
    ("ehlers", "ehlers_highpass_2pole", 0): "warmup_only", ("ehlers", "ehlers_highpass_2pole", 1): "warmup_only",
    ("ehlers", "emdi_hpotter", 0): "standard",                                  # unused input only
    ("ma_filters", "variable_ma", 0): "warmup_only", ("ma_filters", "geometric_mean_ma", 0): "warmup_only",
    ("ma_filters", "uhl_ma", 0): "standard", ("ma_filters", "windowed_ema", 0): "standard",
    ("ma_filters", "binomial_ma", 0): "standard",                               # correct on FMZ (doubles)
    ("ma_filters", "essma", 0): "variant", ("ma_filters", "nma_durschner", 0): "variant",
    ("misc", "gyroscopic_trajectory", 0): "warmup_only", ("misc", "p_signal", 0): "variant", ("misc", "tmo", 0): "variant",
    ("trend", "renko", 3): "variant", ("trend", "renko", 4): "variant",
    ("trend", "td_sequential", 0): "variant", ("trend", "td_sequential", 1): "variant",
    **{("trend", "pivothigh_atr", i): "warmup_only" for i in range(3)},
    ("trend", "standard_error_bands", 0): "warmup_only", ("trend", "avellaneda_stoikov_bands", 0): "variant",
}


def staging_functions():
    out = {}
    sys.path.insert(0, os.path.dirname(ROOT))
    for m in MODULES:
        try:
            mod = importlib.import_module(f"fmz_catalog.{m}")
        except Exception as e:  # module not written yet
            print("skip", m, e)
            continue
        reg = next((v for k, v in vars(mod).items() if k.startswith("EXTRA") and isinstance(v, dict)), {})
        for name, fn in reg.items():
            doc = (fn.__doc__ or "").strip().split("\n")[0]
            out[fn.__name__] = {"module": m, "class": name, "doc": doc, "inputs": fn.inputs, "outputs": fn.outputs, "params": fn.params}
    return out


def reports():
    rep = {}
    for fn in sorted(glob.glob(os.path.join(ROOT, "scan", "impl", "*_report.json"))):
        fam = os.path.basename(fn).replace("_report.json", "")
        try:
            rep[fam] = json.load(open(fn))
        except Exception as e:
            print("bad report", fn, e)
    return rep


def hpotter_files():
    path = os.path.join(ROOT, "scan", "impl", "hpotter_files.jsonl")
    if not os.path.exists(path):
        return {}
    out = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            out[os.path.basename(r["file"])] = r
    return out


def main(usage_json, summary_json):
    usage = json.load(open(usage_json))
    summ = json.load(open(summary_json))
    per_file = summ["per_file"]
    hp = hpotter_files()
    for f, r in hp.items():  # fold in HPotter X-indicator verdicts
        if f in per_file and r.get("verdict") in RANK:
            e = per_file[f]
            if RANK[r["verdict"]] > RANK.get(e["worst"], -1):
                e["worst"] = r["verdict"]
            if r["verdict"] != "standard":
                e["issues"].append({"id": "hpotter", "verdict": r["verdict"], "indicator": r.get("indicator"), "note": r.get("note")})

    funcs = staging_functions()
    reps = reports()
    # fold in bugs the implementation agents found in strategy copies
    for fam, rep in reps.items():
        for name, ent in rep.items():
            if not isinstance(ent, dict):
                continue
            for idx, iss in enumerate(ent.get("strategy_issues") or []):
                sev = SEVERITY.get((fam, name, idx), "bug")
                files = iss.get("files") or []
                if isinstance(files, str):
                    files = [files]
                for f in files:
                    f = os.path.basename(f)
                    if f not in per_file:
                        continue
                    e = per_file[f]
                    if sev != "standard" and not any(x.get("id") == iss.get("id") and x.get("indicator") == name for x in e["issues"]):
                        e["issues"].append({"id": iss.get("id"), "verdict": sev, "indicator": name,
                                            "note": f"[{fam}] {iss.get('issue')}"})
                    if RANK[sev] > RANK.get(e["worst"], -1):
                        e["worst"] = sev

    # ---- impact csv
    with open(os.path.join(ROOT, "impact_by_strategy.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["strategy_file", "language", "worst", "issues"])
        for f in sorted(per_file):
            e = per_file[f]
            iss = "; ".join(f"{x['verdict']}:{x.get('indicator')}: {x.get('note') or ''}" for x in e["issues"])
            w.writerow([f, e["lang"], e["worst"], iss])

    total = len(per_file)
    cnt = collections.Counter(e["worst"] for e in per_file.values())
    by_ind = collections.defaultdict(collections.Counter)
    for e in per_file.values():
        seen = set()
        for x in e["issues"]:
            key = (x["verdict"], (x.get("indicator") or "?").lower())
            if key not in seen:
                by_ind[x["verdict"]][key[1]] += 1
                seen.add(key)

    with open(os.path.join(ROOT, "IMPACT.json"), "w") as fh:
        json.dump({"total": total, "counts": cnt, "by_indicator": {k: v.most_common() for k, v in by_ind.items()}}, fh, indent=1)

    # ---- catalog of staging functions
    lines = ["| Function | Module | Inputs | Outputs | Defaults | What / source |", "|---|---|---|---|---|---|"]
    for name in sorted(funcs):
        f = funcs[name]
        defaults = ", ".join(f"{k}={v!r}" for k, v in f["params"].items())
        lines.append(f"| `{name}` | {f['module']} | {', '.join(f['inputs'])} | {', '.join(f['outputs'])} | {defaults} | {f['doc'].replace('|', '/')} |")
    open(os.path.join(ROOT, "scan", "staging_functions.md"), "w").write("\n".join(lines) + "\n")

    # ---- usage table for built-in / pattern-detected indicators
    ul = ["| Indicator | Strategies | Best implementation |", "|---|---|---|"]
    for key, u in sorted(usage["usage"].items(), key=lambda kv: -len(kv[1]["files"])):
        ul.append(f"| {u['label']} | {len(u['files'])} | {(('fmz_catalog.' if u['tv'].startswith('extra') else 'tv_indicators.') + u['tv']) if u['tv'] else '-'} |")
    open(os.path.join(ROOT, "scan", "usage_table.md"), "w").write("\n".join(ul) + "\n")

    print("strategies", total, dict(cnt))
    print("staging functions", len(funcs), "reports", list(reps))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
