# Maritime route finder

A Django application for exploring ports and shipping lanes, finding a shortest
route between two locations, and displaying it on a full-screen Mapbox map.

## Run locally

The current dependencies have been tested with Python 3.9.6.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
# Configure a public Mapbox token as described below before starting the server.
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`. The database is local and created by `migrate`;
SQLite databases and generated Python caches are not versioned. Map display
requires access to Mapbox, and location searches require Nominatim. These are
development settings; the application is not configured for production hosting.

### Mapbox configuration

Supply your own [public Mapbox access token](https://docs.mapbox.com/help/dive-deeper/access-tokens/)
using the `MAPBOX_PUBLIC_TOKEN` environment variable, or paste it into a local
file named `.mapbox-public-token` in the project root before starting the server.
The file contains only the token and is ignored by Git. The environment variable
takes precedence, including when explicitly set to an empty value.

Use a token beginning with `pk.` with the necessary map read permissions.
Public tokens are intentionally sent to the browser; secret tokens beginning
with `sk.` are never passed to the page. Restrict the public token to your app's
URLs in Mapbox when deploying. No account token is included in this repository's
new commits. Without a configured public token, the map shows an unavailable
message; route calculation and project information remain accessible.

## Map and route controls

- Highlighted circles show **3,582 ports** from the bundled catalogue. Hover over
  a circle to see its name, country (or supplied country code), port code, type
  and coordinates. Click or tap to keep the card open; close it or tap the map
  to dismiss it.
- Shipping lanes appear as faint, slightly blurred lines. A calculated route is
  sharp and drawn above these context layers, with departure/arrival markers.
- **Map layers** controls independently show or hide ports and shipping lanes.
- The floating planner contains the description, route fields and validation
  messages. It can be minimized and minimizes automatically after a successful
  calculation on small screens.
- Zoom, compass, fullscreen, nautical scale, **Show entire route** and **Clear
  route** controls are available. Fullscreen mode keeps the planner accessible.
- **About this project** expands into a large reading panel covering the
  university experiment, Dijkstra's algorithm, datasets, map controls and known
  limitations. Close it with its button, Escape or the backdrop.
- The interface and form feedback are in English, including required-field
  messages. Map labels prefer English names where the basemap supplies them;
  original port names and user-entered place names are preserved.
- **Fastest/Safest** preferences are still placeholders marked as coming soon.

## Project layout

```text
comp600_project/                 Django settings and top-level URLs
dijkstra_alg/
  datasets.py                   Reads the canonical datasets
  routing.py                    Dijkstra and nearest-point algorithms
  views.py                      Location form and route request handling
  map_views.py                  Read-only GeoJSON endpoints
  context_processors.py         Public map configuration for templates
  forms.py, models.py, migrations/
  templates/dijkstra_alg/        Application HTML
  static/dijkstra_alg/
    css/planner.css             Page, control and popup styles
    js/planner.js               Map, form and calculated-route behaviour
    js/map-overlays.js          Port cards and background shipping lanes
    js/interface.js             Project dialog and English form feedback
  tests/                        Python regression and integration tests
data/
  routing-network.geojson        Canonical directed routing network
  ports.geojson                 Prepared port catalogue
  sources/                      Original port workbook and shipping source
scripts/                        Reproducible data preparation
tests/frontend/                 Map interaction unit tests (Node.js)
docs/                           Original project reports and design documents
archive/                        Historical prototypes, templates and environment
```

Django discovers the app's namespaced templates and static files. `STATIC_URL`
is absolute so assets also load on `/input`. A deployment can collect these
assets with `python manage.py collectstatic`; generated `staticfiles/` stays
outside version control.

## Data and routing behaviour

See [data/README.md](data/README.md) for source details and catalogue regeneration.
The port catalogue and route network are separate datasets. Port circles are
actual catalogue locations; offshore network waypoints are not labelled as
ports. The catalogue is a historical snapshot, and its ports are not guaranteed
to be connected to the routing network. Missing descriptive fields are displayed
as not listed, without inferring operating status or availability.

The current map overlays do **not** change route calculation:

- Location searches use Nominatim and snap to the nearest network endpoint.
- Nearest-point matching retains squared longitude/latitude distance.
- Dijkstra follows the directed segments and minimizes `Length0`. Duplicate
  connections use the shortest segment and its matching map geometry.
- Unreachable routes, unknown locations and service failures return clear form
  messages. Locations matching the same endpoint do not create an invalid line.
- Route coordinates belong to each request; no shared output file is written.
- Mercator projection and padding keep the calculated route visible beside the
  planner, including high-latitude routes.

The background endpoints `/api/map/ports/` and `/api/map/network/` return
GeoJSON with a one-hour browser cache policy. They require no geocoding. Routing
continues to use the original complete dataset on the server.

## Verify changes

```sh
python manage.py check
python manage.py test dijkstra_alg
node --test tests/frontend/*.test.js
```

Python tests cover routing, nearest-point lookup, form validation, map-data
integrity, static-file discovery and complete requests using the actual network.
Geocoding is mocked, so the suite requires no external service or database.
Frontend unit tests require Node.js 18 or later and exercise port hover, click/tap, closing, layer visibility and
safe handling of catalogue text. Browser checks also require Mapbox access.
