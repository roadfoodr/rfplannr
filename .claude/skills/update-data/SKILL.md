---
name: update-data
description: Process a new Roadfood source spreadsheet through the geocoding pipeline and update the live SQLite database. Use when the user wants to update the data, process a new spreadsheet version, or run process_roadfood. Triggers on requests like "update the data", "process the new spreadsheet", "run the wrangle script".
---

# Update Data

Processes a new source `.xlsx` from `data_working/` through geocoding and updates `data/rfplannr.sqlite`.

## Workflow

### 1. Discover files

```bash
python .claude/skills/update-data/scripts/discover.py
```

- **Exit 0**: Parse `NEW_FILE_BASE` and `OLD_FILE_BASE` from stdout and proceed.
- **Exit 2 (ambiguous)**: Two candidates disagree on "latest." Relay both to the user and ask which to use. Then proceed with the chosen `NEW_FILE_BASE` and the `OLD_FILE_BASE` from the script output.
- **Exit 3 (already current)**: The latest source xlsx was already processed. Tell the user and ask if they want to skip to the deploy step anyway. If yes, that confirmation counts for step 5 — do not ask again.
- **Exit 1 (error)**: Report the error to the user and stop.

### 2. Copy source xlsx to data/

```bash
cp "data_working/{NEW_FILE_BASE}.xlsx" "data/{NEW_FILE_BASE}.xlsx"
```

### 3. Run geocoding

```bash
uv run --project wrangle wrangle/process_roadfood.py {NEW_FILE_BASE}
```

This makes Google API calls and may be slow. Monitor output for errors. Each failed row prints a timestamped message but does not abort the run.

### 4. Shuffle files

```bash
python .claude/skills/update-data/scripts/shuffle.py {NEW_FILE_BASE} {OLD_FILE_BASE}
```

This:
- Archives `data/rfplannr.sqlite` → `data_working/{OLD_FILE_BASE}_GEO.sqlite`
- Renames `data/{NEW_FILE_BASE}_GEO.sqlite` → `data/rfplannr.sqlite`
- Moves `data/{NEW_FILE_BASE}_GEO.xlsx` → `data_working/`

### 5. Deploy

Ask the user to confirm before proceeding. Then sync non-public config from `.env`, rebuild the tarball, and deploy.

If `.env` contains `PERSONAL_MODE_PATH`, set the matching Heroku config var before creating the build:

```bash
heroku config:set PERSONAL_MODE_PATH={PERSONAL_MODE_PATH} -a rfplannr
```

Do not include `.env` in the tarball. Heroku reads `PERSONAL_MODE_PATH` from config vars at runtime.

```bash
tar -czf rfplannr.tar.gz .python-version .flaskenv .gitignore Procfile requirements.txt rfplannr.py data/rfplannr.sqlite static/ templates/
heroku builds:create --source-tar rfplannr.tar.gz -a rfplannr
```

### 7. Report results

Confirm to the user which files were processed, that the tarball was rebuilt, and that the deploy was submitted. Note that Heroku builds run asynchronously — the app will be live once the build completes.
