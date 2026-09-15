# Dataset sources

## Routing network

`routing-network.geojson` is the original application dataset, moved from the
repository root without changing its contents. It contains 8,273 directed
segments. The embedded metadata attributes the shipping network to the **Oak
Ridge National Labs CTA Transportation Network Group**, published in 2000.
The original downloaded representation is retained at
`sources/shipping-network-original.geojson`.

`From Node0`, `To Node0` and `Length0` retain their original routing meaning.
Coordinates use GeoJSON order: **longitude, latitude**. Duplicate copies formerly
stored under the app, prototypes and project documents have been consolidated.

## Port catalogue

`ports.geojson` is generated from the existing `sources/portlist.xls`, worksheet
`wld_trs_ports_wfp`. No additional port records have been downloaded or inferred.
All 3,582 rows are retained, including sea, river, lake and unspecified types.
The source has 14 unnamed records, shown as **Unnamed port**. Blank country names
remain blank; the popup uses the supplied country code if available. Coordinates
come directly from the workbook's longitude and latitude fields.

Each feature ID is its one-based spreadsheet row number (the first port is row
2). This makes records traceable to the source and provides stable hover IDs.
The small GeoJSON properties are name, port code, country, country code and type.
Historical operational-status fields are intentionally not presented as current
port status.

Rebuild the catalogue after an intentional source update:

```sh
python -m pip install -r requirements-data.txt
python scripts/build_port_catalogue.py
```

The converter validates coordinate bounds and fails on invalid coordinates.
`xlrd` is needed only for regeneration; it is not a web application dependency.
The checked-in catalogue is deterministic and ready to serve after cloning.
