import requests
import json
import sys


if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]

url = f"http://{ip}:{port}/api/leases/state/"
request_data_customer_type= [
    {
        "name": "Pre-reserva",
        "next_state": [2,5]
    },
    {
        "name": "Reserva",
        "next_state": [3,5]
    },
    {
        "name": "Alquilado",
        "next_state": [4,5]
    },
    {
        "name": "Concluido"
    },
    {
        "name": "Anulado"
    },
]
for data in request_data_customer_type:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.json())