"""Convert the bundled legacy XLS port catalogue into reproducible GeoJSON.

Install requirements-data.txt, then run this file from any working directory.
The web application reads the checked-in GeoJSON and does not need xlrd.
"""

import json
import math
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[1]


def catalogue(source):
    sheet = xlrd.open_workbook(str(source)).sheet_by_name('wld_trs_ports_wfp')
    headers = sheet.row_values(0)
    features = []
    for index in range(1, sheet.nrows):
        row = dict(zip(headers, sheet.row_values(index)))
        longitude, latitude = float(row['longitude']), float(row['latitude'])
        if not (math.isfinite(longitude) and math.isfinite(latitude)
                and -180 <= longitude <= 180 and -90 <= latitude <= 90):
            raise ValueError(f'Invalid coordinates in source row {index + 1}')
        features.append({
            'type': 'Feature',
            'id': index + 1,
            'properties': {
                'name': str(row['portname']).strip() or 'Unnamed port',
                'code': str(row['code']).strip(),
                'country': str(row['country']).strip(),
                'country_code': str(row['iso3'] or row['iso3_op']).strip(),
                'port_type': str(row['prttype']).strip(),
            },
            'geometry': {'type': 'Point', 'coordinates': [longitude, latitude]},
        })
    return {'type': 'FeatureCollection', 'features': features}


if __name__ == '__main__':
    result = catalogue(ROOT / 'data/sources/portlist.xls')
    destination = ROOT / 'data/ports.geojson'
    destination.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n',
                           encoding='utf-8')
    print(f'Wrote {len(result["features"])} ports to {destination}')
