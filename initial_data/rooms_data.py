import requests
import json
import sys
import os

if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]
url = f"http://{ip}:{port}/api/rooms/"
script_directory = os.path.dirname(os.path.realpath(__file__))
media_directory = os.path.join(script_directory, "..", "media")

requests_data = [
    {
            "name": "SALÓN BIÓGRAFO",
            "capacity": 200,
            "warranty": 1000,
            "is_active": True,
            "property": 1,
            "group":1
    },
    {
            "name": "SALÓN GUZMÁN DE ROJAS",
            "capacity": 250,
            "warranty": 500,
            "is_active": True,
            "property": 1,
            "group":2
    },
    {
            "name": "SALON GOBELINO",
            "capacity": 100,
            "warranty": 700,
            "is_active": True,
            "property": 1,
            "group":3
    },
    {
            "name": "AREA DE EXPOSICION",
            "capacity": 80,
            "warranty": 200,
            "is_active": True,
            "property": 1,
            "group":4
    },
    {
            "name": "AMBIENTES INTERIORES Y EXTERIORES ",
            "capacity": 300,
            "warranty": 400,
            "is_active": True,
            "property": 2,
            "group":5
    },
    {
            "name": "AMBIENTES INTERIORES",
            "capacity": 200,
            "warranty": 100,
            "is_active": True,
            "property": 2,
            "group":5
    },
    {
            "name": "AMBIENTES EXTERIORES",
            "capacity": 300,
            "warranty": 400,
            "is_active": True,
            "property": 2,
            "group":5
    }
]

for data in requests_data:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url,data={
                                "name": data["name"],
                                "capacity":data["capacity"],
                                "warranty":data["warranty"],
                                "is_active":data["is_active"],
                                "property":data["property"],
                                "group":data["group"]
                                }, headers=headers)
    print(response.status_code, response.json())
