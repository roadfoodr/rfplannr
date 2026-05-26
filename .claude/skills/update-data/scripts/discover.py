"""
Discover the latest source xlsx in data_working/ and determine the old FILE_BASE.
Outputs NEW_FILE_BASE and OLD_FILE_BASE lines to stdout.
Exit codes: 0=ok, 1=error, 2=ambiguous (relay candidates to user), 3=already up to date.
"""
import sys
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / 'data'
DATA_WORKING_DIR = PROJECT_ROOT / 'data_working'


def parse_filename_date(stem):
    m = re.search(r'Roadfood_MDP_(\d{2})(\d{2})(\d{2})$', stem)
    if m:
        month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3)) + 2000
        try:
            return datetime(year, month, day)
        except ValueError:
            return None
    return None


candidates = [
    (f, parse_filename_date(f.stem), datetime.fromtimestamp(f.stat().st_mtime))
    for f in DATA_WORKING_DIR.glob('*.xlsx')
    if '_GEO' not in f.stem
]

if not candidates:
    print("ERROR: No source .xlsx files found in data_working/", file=sys.stderr)
    sys.exit(1)

dated = sorted([c for c in candidates if c[1]], key=lambda x: x[1], reverse=True)
by_mod = sorted(candidates, key=lambda x: x[2], reverse=True)

latest_by_fn = dated[0] if dated else None
latest_by_mod = by_mod[0]

if latest_by_fn and latest_by_fn[0] != latest_by_mod[0]:
    print(f"AMBIGUOUS: Latest by filename date: {latest_by_fn[0].stem} ({latest_by_fn[1].date()})")
    print(f"AMBIGUOUS: Latest by mod date:      {latest_by_mod[0].stem} ({latest_by_mod[2].date()})")
    sys.exit(2)

chosen = latest_by_fn if latest_by_fn else latest_by_mod
new_file_base = chosen[0].stem

# Determine old FILE_BASE from newest _GEO.xlsx in data_working
geo_xlsx = sorted(DATA_WORKING_DIR.glob('*_GEO.xlsx'), key=lambda f: f.stat().st_mtime, reverse=True)
if geo_xlsx:
    old_file_base = geo_xlsx[0].stem.replace('_GEO', '')
    if old_file_base == new_file_base:
        print(f"ALREADY_CURRENT: {new_file_base} has already been processed.")
        sys.exit(3)
    print(f"NEW_FILE_BASE={new_file_base}")
    print(f"OLD_FILE_BASE={old_file_base}")
else:
    print(f"NEW_FILE_BASE={new_file_base}")
    sqlite = DATA_DIR / 'rfplannr.sqlite'
    if sqlite.exists():
        mod = datetime.fromtimestamp(sqlite.stat().st_mtime)
        print(f"OLD_FILE_BASE=rfplannr_archived_{mod.strftime('%Y%m%d')}")
    else:
        print("OLD_FILE_BASE=unknown")
    print(f"NEW_FILE_BASE={new_file_base}")
