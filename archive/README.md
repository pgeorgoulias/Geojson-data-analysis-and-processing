# Historical project material

This directory preserves early prototypes, unused templates, the original
Windows Conda environment export and an old route-output example. These files
are reference material and are not loaded by the Django application.

The old route-output example consists of concatenated JSON objects rather than a
single valid JSON document. Current routing returns coordinates per request and
does not read or overwrite it. The Python prototypes use the canonical network
under `data/` where needed; their original experiments are otherwise preserved.

Active code is under `dijkstra_alg/`. Install `requirements.txt` for the current
application rather than the archived Windows environment export.
