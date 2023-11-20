import requests
import json
import sys
import os

if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]
url = f"http://{ip}:{port}/api/product/hour-range/"
script_directory = os.path.dirname(os.path.realpath(__file__))
media_directory = os.path.join(script_directory, "..", "media")

requests_data = [
    {
        "time":8
    },
    {
        "time":4
    }
]

for data in requests_data:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, data={"time": data["time"]}, headers=headers)
    print(response.status_code, response.json())