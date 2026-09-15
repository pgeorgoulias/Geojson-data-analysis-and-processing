import json
from pathlib import Path

file1 = json.load(open(Path(__file__).resolve().parents[2] / "data/routing-network.geojson"))

coordinates = file1[0]["features"]
print (coordinates)