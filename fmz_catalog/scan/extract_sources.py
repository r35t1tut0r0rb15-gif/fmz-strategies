import glob, re, json, collections, sys
out = collections.defaultdict(list)
for f in glob.glob('*.md'):
    t = open(f, encoding='utf-8', errors='ignore').read()
    m = re.search(r'^> Source \(([^)]+)\)\s*\n(.*?)(?=^> Detail|\Z)', t, re.S | re.M)
    if not m: continue
    lang, code = m.group(1), m.group(2)
    code = re.sub(r'^```\w*\s*$', '', code, flags=re.M)
    out[lang].append((f, code))
json.dump({k: v for k, v in out.items()}, open(sys.argv[1], 'w'))
print({k: len(v) for k, v in out.items()})
