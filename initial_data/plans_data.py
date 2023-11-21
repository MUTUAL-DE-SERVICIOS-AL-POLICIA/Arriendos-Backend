import requests
import json
import sys


if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]

url = f"http://{ip}:{port}/api/plans/"

request_data_requirements = [
    {
        "plan_name":"Plan A",
        "plan_discount":25,
        "rooms_min":8,
        "rooms_max":15
    },
    {
        "plan_name":"Plan B",
        "plan_discount":50,
        "rooms_min":16,
        "rooms_max":100
    }
]
for data in request_data_requirements:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.json())