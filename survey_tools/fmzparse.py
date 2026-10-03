"""Parse FMZ strategy markdown files (static text only; nothing is executed)."""
import re
from pathlib import Path

SECTION_RE = re.compile(r'^> (Name|Author|Strategy Description|Strategy Arguments|Source \(([^)]+)\)|Detail|Last Modified)\s*$', re.M)


def parse(path):
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    marks = [(m.start(), m.end(), m.group(1), m.group(2)) for m in SECTION_RE.finditer(text)]
    sec = {}
    lang = None
    for i, (s, e, name, lg) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        body = text[e:end].strip('\n')
        if lg:
            lang = lg
            name = 'Source'
        sec.setdefault(name, body)
    src = sec.get('Source', '')
    m = re.search(r'```[^\n]*\n(.*?)\n```', src, re.S)
    code = m.group(1) if m else src
    detail = sec.get('Detail', '').strip()
    idm = re.search(r'fmz\.com/strategy/(\d+)', detail)
    return {
        'file': Path(path).name,
        'name': sec.get('Name', '').strip(),
        'author': sec.get('Author', '').strip(),
        'lang': lang or '',
        'code': code,
        'args': sec.get('Strategy Arguments', ''),
        'fmz_id': int(idm.group(1)) if idm else None,
        'detail_url': idm.group(0) and 'https://www.' + idm.group(0) if idm else detail,
        'last_modified': sec.get('Last Modified', '').strip(),
        'text': text,
    }
