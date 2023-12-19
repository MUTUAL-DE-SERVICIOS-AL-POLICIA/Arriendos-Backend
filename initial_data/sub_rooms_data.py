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
url = f"http://{ip}:{port}/api/rooms/sub_rooms/"
script_directory = os.path.dirname(os.path.realpath(__file__))
media_directory = os.path.join(script_directory, "..", "media")

requests_data = [
    {
    "room": 1,
    "name": "Lobby principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Guardarropa",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Baño hall",
    "quantity": 2,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Salón principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Escenario",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Baños interior salón",
    "quantity": 2,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Cocina",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 1,
    "name": "Pasillo",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 2,
    "name": "Pasillo",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 2,
    "name": "Depósito",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 2,
    "name": "Baño salón",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 2,
    "name": "Salón Principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 3,
    "name": "Salón Principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 3,
    "name": "Baño Salón",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 4,
    "name": "Hall Principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Salón Principal (planta baja)",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Bar",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Mostrador del bar",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Cabina de Sonido",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Baños Salón Principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Salón Secundario (Planta Alta)",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Ambiente complementario (Planta Alta)",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Baños Salón Secundario (Planta Alta)",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Cocina",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 5,
    "name": "Depósito (interior cocina)",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Jardin Principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Mesón jardin principal",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Pista",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Escenario",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Piscina",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Jardín Secundario",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Baños Jardín",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Parque infantil",
    "quantity": 1,
    "state": "BUENO"
    },
    {
    "room": 6,
    "name": "Depósito (Exterior cocina)",
    "quantity": 1,
    "state": "BUENO"
    }
]

for data in requests_data:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, data={"room": data["room"],"name":data["name"], "quantity":data["quantity"],"state":data["state"]}, headers=headers)
    print(response.status_code, response.json())
