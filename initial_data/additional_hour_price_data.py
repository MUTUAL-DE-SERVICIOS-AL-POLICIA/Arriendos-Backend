import requests
import json
import sys
if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)
ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]
url = f"http://{ip}:{port}/api/product/additional_hour/"

requests_data = [
    {
    "mount": 450,
    "state": True,
    "hourRange": 1,
    "room": 1
    },
    {
    "mount": 570,
    "state": True,
    "hourRange": 2,
    "room": 1
    },
    {
    "mount": 220,
    "state": True,
    "hourRange": 1,
    "room": 2
    },
    {
    "mount": 250,
    "state": True,
    "hourRange": 2,
    "room": 2
    },
    {
    "mount": 110,
    "state": True,
    "hourRange": 1,
    "room": 3
    },
    {
    "mount": 125,
    "state": True,
    "hourRange": 2,
    "room": 3
    },
    {
    "mount": 235,
    "state": True,
    "hourRange": 1,
    "room": 4
    },
    {
    "mount": 375,
    "state": True,
    "hourRange": 1,
    "room": 5
    },
    {
    "mount": 500,
    "state": True,
    "hourRange": 2,
    "room": 5
    },
    {
    "mount": 275,
    "state": True,
    "hourRange": 1,
    "room": 6
    },
    {
    "mount": 375,
    "state": True,
    "hourRange": 2,
    "room": 6
    },
    {
    "mount": 615,
    "state": True,
    "hourRange": 1,
    "room": 7
    },
    {
    "mount": 750,
    "state": True,
    "hourRange": 2,
    "room": 7
    }
]
for data in requests_data:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.json())