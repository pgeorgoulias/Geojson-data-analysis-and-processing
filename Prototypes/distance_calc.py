import json

file1 = json.load(open("parsed_data.json"))

coordinates = file1[0]["features"]
print (coordinates)