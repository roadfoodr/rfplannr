"""
Shuffle files after geocoding completes.
Usage: shuffle.py NEW_FILE_BASE OLD_FILE_BASE
  - Archives data/rfplannr.sqlite -> data_working/{OLD_FILE_BASE}_GEO.sqlite
  - Renames data/{NEW_FILE_BASE}_GEO.sqlite -> data/rfplannr.sqlite
  - Moves data/{NEW_FILE_BASE}_GEO.xlsx -> data_working/
"""
import sys
import shutil
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: shuffle.py NEW_FILE_BASE OLD_FILE_BASE", file=sys.stderr)
    sys.exit(1)

NEW_FILE_BASE, OLD_FILE_BASE = sys.argv[1], sys.argv[2]

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / 'data'
DATA_WORKING_DIR = PROJECT_ROOT / 'data_working'

old_sqlite = DATA_DIR / 'rfplannr.sqlite'
if old_sqlite.exists():
    dest = DATA_WORKING_DIR / f'{OLD_FILE_BASE}_GEO.sqlite'
    shutil.move(str(old_sqlite), str(dest))
    print(f"Archived rfplannr.sqlite -> data_working/{dest.name}")
else:
    print("WARNING: data/rfplannr.sqlite not found, skipping archive step")

new_sqlite = DATA_DIR / f'{NEW_FILE_BASE}_GEO.sqlite'
if new_sqlite.exists():
    new_sqlite.rename(DATA_DIR / 'rfplannr.sqlite')
    print(f"Renamed {new_sqlite.name} -> rfplannr.sqlite")
else:
    print(f"ERROR: {new_sqlite.name} not found in data/", file=sys.stderr)
    sys.exit(1)

geo_xlsx = DATA_DIR / f'{NEW_FILE_BASE}_GEO.xlsx'
if geo_xlsx.exists():
    shutil.move(str(geo_xlsx), str(DATA_WORKING_DIR / geo_xlsx.name))
    print(f"Moved {geo_xlsx.name} -> data_working/")
else:
    print(f"WARNING: {geo_xlsx.name} not found in data/")
