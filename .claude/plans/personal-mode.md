# Personal Mode Plan

## Goal

Make `rfplannr` public by default while preserving MDP's visited/unvisited view behind an obscure, lightweight personal mode.

Public mode should show:

1. A permanently closed layer.
2. A single Roadfood layer for all non-closed locations, using blue markers.

Personal mode should preserve the current MDP-specific behavior:

1. Visited layer, using current green marker behavior.
2. Unvisited layer, using current blue marker behavior.
3. Permanently closed layer, using current red marker behavior.

This should not add accounts, cookies, sessions, local storage, or authentication. The mode should persist only by carrying an obscure URL prefix through app-generated links.

The personal URL prefix should come from an environment variable so it does not need to be hardcoded in source. MDP will probably use `mdp` as the value:

```text
PERSONAL_MODE_PATH=mdp
```

## Recommended Approach

Use a hidden URL prefix for personal mode. The examples below assume `PERSONAL_MODE_PATH=mdp`:

```text
/                 public home
/map              public map
/map/<hashid>     public map permalink
/table            public table
/table/<hashid>   public table permalink
/export           public spreadsheet export
/export/<hashid>  public spreadsheet export

/mdp                 personal home
/mdp/map             personal map
/mdp/map/<hashid>    personal map permalink
/mdp/table           personal table
/mdp/table/<hashid>  personal table permalink
/mdp/export          personal spreadsheet export
/mdp/export/<hashid> personal spreadsheet export
```

The `/mdp` prefix is not intended as security. It is just an unadvertised entry point. Anyone who knows the URL can view personal mode, which is acceptable for this project.

Do not hardcode `mdp` throughout the application. Read it once at app startup, validate it as a single safe URL segment, and use that configured value to register personal routes and generate personal-mode links.

## How Mode Persistence Works

No browser state is needed. The current route determines the mode.

When rendering a page, pass a template variable such as:

```python
personal_mode=True
```

for `/<PERSONAL_MODE_PATH>/...` routes and:

```python
personal_mode=False
```

for public routes.

Templates and JavaScript-generated URLs should use mode-aware URLs. In personal mode, app-generated links should point back under `/mdp`; in public mode, links should remain on the normal public routes.

Examples:

```text
Public map start over:        /
Personal map start over:      /mdp

Public table permalink:       /table/<hashid>
Personal table permalink:     /mdp/table/<hashid>

Public map permalink:         /map/<hashid>
Personal map permalink:       /mdp/map/<hashid>

Public export:                /export/<hashid>
Personal export:              /mdp/export/<hashid>
```

This is the entire persistence mechanism: if the user enters through `/<PERSONAL_MODE_PATH>`, every generated link keeps them under that same prefix.

## Implementation Notes

### Flask Routes

Keep the existing public routes as the default behavior.

Add personal-mode equivalents for home, map, table, and export. These can call the same underlying helper functions with a `personal_mode` argument instead of duplicating logic.

Read the personal path from the environment:

```python
PERSONAL_MODE_PATH = os.environ.get("PERSONAL_MODE_PATH", "").strip("/")
```

Validate it before registering routes. Keep it to one URL path segment made of letters, numbers, underscores, or hyphens:

```python
if PERSONAL_MODE_PATH and not re.fullmatch(r"[A-Za-z0-9_-]+", PERSONAL_MODE_PATH):
    raise ValueError("PERSONAL_MODE_PATH must be one URL segment")
```

If `PERSONAL_MODE_PATH` is unset, do not register personal routes. Public mode should still work.

The current code has overlapping `/map` GET routes: one route renders the map and another route calls `recall_selection_all()`. When implementing personal mode, clean this up into shared render helpers and unambiguous route handlers instead of copying that overlap into the new personal routes.

Possible shape:

```python
@app.route("/")
def home_page():
    return render_home(personal_mode=False)

@app.route(f"/{PERSONAL_MODE_PATH}")
def personal_home_page():
    return render_home(personal_mode=True)

@app.route("/map", methods=["GET", "POST"])
@app.route("/map/<string:hashid>")
def public_map(...):
    return render_map(..., personal_mode=False)

@app.route(f"/{PERSONAL_MODE_PATH}/map", methods=["GET", "POST"])
@app.route(f"/{PERSONAL_MODE_PATH}/map/<string:hashid>")
def personal_map(...):
    return render_map(..., personal_mode=True)
```

The exact function names can follow the existing style in `rfplannr.py`. The important point is to centralize the logic so public and personal routes do not drift apart.

For conditional personal route registration, either of these patterns is fine:

1. Put the personal route decorators inside an `if PERSONAL_MODE_PATH:` block.
2. Use `app.add_url_rule()` with explicit endpoint names.

`app.add_url_rule()` may be slightly clearer for dynamically configured paths, but there is no strong project preference.

Make sure the personal map route supports both `GET` and `POST`. The `POST` handler is needed for state-filter form submissions from the personal home page.

### URL Generation

Add a small helper function that selects public or personal endpoints based on `personal_mode`.

Example:

```python
def mode_url(endpoint, personal_mode=False, **values):
    if personal_mode:
        endpoint = f"personal_{endpoint}"
    return url_for(endpoint, **values)
```

This helper is optional. It may be simpler to pass explicit URLs into each template:

```python
home_url = url_for("personal_home_page" if personal_mode else "home_page")
table_url = url_for("personal_table_selection" if personal_mode else "table_selection", hashid="")
export_url = url_for("personal_export_selection" if personal_mode else "export_selection", hashid=hashid)
map_url = url_for("personal_recall_selection" if personal_mode else "recall_selection", hashid=hashid)
```

The current JavaScript already receives `table_url` and `home_url` from `map.html`; keep that pattern and make those variables mode-aware.

Avoid hardcoded endpoint calls in templates when the target depends on mode. Pass explicit URL strings from Flask instead.

### Home Page

Use the existing `templates/index.html` for both public and personal home pages.

The only required change is making the form action mode-aware:

```html
<form class="pure-form" action="{{ map_form_url }}" method="post">
```

Public home should pass `/map`.

Personal home should pass `/<PERSONAL_MODE_PATH>/map`.

The personal form target must accept `POST`, just like the public `/map` state-filter route.

No visible toggle is needed. Optionally, the personal home page may show a tiny private-only label such as `MDP mode`, but the simplest version should keep the UI identical.

### Map Behavior

The map marker data should include enough information for the template to build either public or personal layers.

Current personal behavior:

```python
red   = closed
green = visited
blue  = unvisited
```

New public behavior:

```python
red  = closed
blue = all non-closed Roadfood locations
```

In `templates/map.html`, branch layer setup by `personal_mode`.

Public mode:

```javascript
var roadfoodLayer = L.layerGroup();
var closedLayer = L.layerGroup();

controlBox.addOverlay(roadfoodLayer, "roadfood");
controlBox.addOverlay(closedLayer, "closed");
```

Personal mode:

```javascript
var visitedLayer = L.layerGroup();
var unvisitedLayer = L.layerGroup();
var closedLayer = L.layerGroup();

controlBox.addOverlay(visitedLayer, "visited");
controlBox.addOverlay(unvisitedLayer, "unvisited");
controlBox.addOverlay(closedLayer, "closed");
```

The marker selection, delete-selected, delete-not-visible, and table-view commands should continue to operate on `allMarkerGroup`, so those features should not need much change.

### Table And Export

Public table/export can still include the existing columns unless there is a later decision to hide personal fields. The main requirement for this phase is that links generated from personal table/export routes preserve the configured personal prefix.

In `templates/table_view.html`, make the map/table/export links mode-aware by passing the URLs from Flask instead of hardcoding endpoint names in the template.

The current `table_view.html` has hardcoded `url_for()` calls for:

```text
recall_selection
table_selection
export_selection
```

Replace those with template variables passed by Flask so the same template can render public and personal links correctly.

Example template variables:

```python
map_permalink_url
table_permalink_url
export_url
```

### Hashids

Do not encode the mode into the hashid. Keep hashids focused only on selected restaurant IDs.

The mode belongs in the URL prefix:

```text
/map/<hashid>
/mdp/map/<hashid>
```

This keeps public and personal permalinks easy to reason about.

### Local Environment

Store the personal path in the repo's existing `.env` file for local use:

```text
PERSONAL_MODE_PATH=mdp
```

`.env` is already ignored by Git, so the configured path will not appear in GitHub source. If the app should load `.env` automatically during local `flask run`, verify that `python-dotenv` is installed. If it is not already present transitively, add `python-dotenv` to `requirements.txt`.

Currently `python-dotenv` is not listed in `requirements.txt`. Add it so `flask run` loads `.env` automatically during local development.

### Heroku Deployment

Heroku does not read the repo `.env` file directly. The app receives environment variables from Heroku config vars.

Before or during deploy, sync the local `.env` value into Heroku:

```text
heroku config:set PERSONAL_MODE_PATH=mdp -a rfplannr
```

Changing this config var restarts the Heroku dyno but does not require rebuilding `rfplannr.tar.gz`. A rebuild is only needed when the source code, templates, static files, requirements, or database change.

Update the deploy skill at `.claude/skills/update-data/SKILL.md` so the deploy step reads `PERSONAL_MODE_PATH` from `.env` and ensures the Heroku config var is set before running `heroku builds:create`. The skill should not include `.env` in the tarball.

Suggested deploy-skill behavior:

1. Read `.env` and extract `PERSONAL_MODE_PATH`.
2. If present, run `heroku config:set PERSONAL_MODE_PATH=<value> -a rfplannr`.
3. Build the tarball without `.env`, as it does today.
4. Submit the Heroku build.

Keep any future secrets/config values out of `rfplannr.tar.gz` unless they are intentionally public.

## Acceptance Criteria

1. Visiting `/` and submitting states opens public mode.
2. Visiting `/map` directly opens public mode.
3. Public mode has only `roadfood` and `closed` overlays.
4. Public non-closed markers are blue, regardless of MDP visited status.
5. With `PERSONAL_MODE_PATH=mdp`, visiting `/mdp` and submitting states opens personal mode.
6. With `PERSONAL_MODE_PATH=mdp`, visiting `/mdp/map` directly opens personal mode.
7. Personal mode keeps the current `visited`, `unvisited`, and `closed` overlays.
8. In personal mode, start-over, table-view, map permalink, table permalink, and export links all stay under the configured personal prefix.
9. In public mode, those same links stay on the public routes.
10. No cookies, sessions, local storage, login, or new database tables are added.

## Suggested Test Pass

Manual checks should be enough for this lightweight repo:

1. Start the Flask app locally.
2. Open `/` and submit a blank state filter. Confirm public map layers and marker colors.
3. Set `PERSONAL_MODE_PATH=mdp`, then open `/mdp` and submit a blank state filter. Confirm personal map layers and marker colors.
4. In public mode, remove some markers and open the table view. Confirm the URL is `/table/<hashid>`.
5. In personal mode, remove some markers and open the table view. Confirm the URL is `/mdp/table/<hashid>`.
6. From each table view, test map permalink and export links. Confirm the route prefix is preserved.
