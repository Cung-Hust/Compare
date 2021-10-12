import json
t = """{
  "RQI": "vietanh",
  "TYPCMD": "ControlDevice",
  "Device": [[1, 2, 3]],
  "groups": [
    {
      "group": 10,
      "Type": 1
    }
  ],
  "Relay": true,
  "DIM": 100
}"""

json_data = json.loads(t)
a = json_data["RQI"]
b = json_data["RQI"]

print(hex(id(a)))
print(hex(id(b)))
