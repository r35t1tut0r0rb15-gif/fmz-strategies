"""Run one batch's static steps in order (start it at low priority: cmd /c start /low /b /wait ...):
manifest_add (batches\\<batch>.json) -> make_port_files -> py_compile of the batch's new modules (bytecode to a
scratch folder, nothing in the repo) -> check_ports -> summarize. Stops at the first failure.
Usage: python -X utf8 -I batch_checks.py <batch> [--no-manifest]"""
import json
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import heartbeat  # noqa: E402

TOOLS = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[1]  # repository root (cloud copy, 2026-10-21)
PY = sys.executable


def run(args, **kw):
    heartbeat.beat(" ".join(str(a) for a in args[-2:]))
    r = subprocess.run([PY, "-X", "utf8", "-I", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", **kw)
    out = (r.stdout + r.stderr).strip()
    print(out[-3000:])
    if r.returncode:
        raise SystemExit(f"FAILED: {args} (exit {r.returncode})")
    return out


def main():
    batch = sys.argv[1]
    spec = json.loads((TOOLS / "batches" / f"{batch}.json").read_bytes().decode("utf-8"))
    if "--no-manifest" not in sys.argv:
        run([str(TOOLS / "manifest_add.py"), str(TOOLS / "batches" / f"{batch}.json")])
    run(["survey_tools/make_port_files.py"])
    slugs = {}
    import csv
    for r in csv.DictReader(open(REPO / "screening.csv", encoding="utf-8")):
        slugs[r["fmz_id"]] = r["slug"]
    scratch = Path(tempfile.gettempdir()) / "fmz_C_pycompile"
    scratch.mkdir(exist_ok=True)
    n = 0
    for fid in spec.get("sizing", {}):
        mod = REPO / "ports" / slugs[fid] / "module.py"
        py_compile.compile(str(mod), cfile=str(scratch / f"{fid}.pyc"), doraise=True)
        n += 1
    print(f"py_compile: {n} modules OK")
    # FMZ-C self-check (2026-10-16): the docstring's source facts must match the corpus file
    import re
    rows = {r["fmz_id"]: r for r in csv.DictReader(open(REPO / "screening.csv", encoding="utf-8"))}
    bad = []
    for fid in spec.get("sizing", {}):
        mod = (REPO / "ports" / slugs[fid] / "module.py").read_bytes().decode("utf-8")
        src = (REPO / rows[fid]["file"]).read_bytes().decode("utf-8")
        if rows[fid]["last_modified"] not in mod:
            bad.append(f"{fid}: last modified {rows[fid]['last_modified']} not in the docstring")
        import ast
        tree = ast.parse(mod)
        grid = next(ast.literal_eval(nd.value) for nd in tree.body if isinstance(nd, ast.Assign)
                    and any(getattr(t, "id", "") == "GRID" for t in nd.targets))
        ntr = 1
        for v in grid.values():
            ntr *= len(v)
        mt = re.search(r"GRID below \((\d+) trials?\)", mod)
        if not mt or int(mt.group(1)) != ntr:
            bad.append(f"{fid}: docstring trial count {mt.group(1) if mt else None} != GRID product {ntr}")
        notes = (REPO / "ports" / slugs[fid] / "PORT_NOTES.md").read_bytes().decode("utf-8")
        mn = re.search(r"\*\*(\d+) trials?\*\*", notes)
        if not mn or int(mn.group(1)) != ntr:
            bad.append(f"{fid}: PORT_NOTES trial count {mn.group(1) if mn else None} != GRID product {ntr}")
        if rows[fid]["lang"] == "PineScript":
            v = re.search(r"@version\s*=\s*(\d)", src)
            want = f"PineScript v{v.group(1)}" if v else "no @version line"
            if want not in mod:
                bad.append(f"{fid}: docstring should say {want!r}")
    if bad:
        print("\n".join(bad))
        raise SystemExit("source facts in docstrings do not match the corpus")
    print(f"source facts: {n} docstrings match the corpus (last modified, Pine version)")
    out = run(["survey_tools/check_ports.py"])
    if " 0 with problems" not in out:
        raise SystemExit("check_ports reported problems")
    run(["survey_tools/summarize.py"])
    print("ALL STEPS OK")


if __name__ == "__main__":
    main()
