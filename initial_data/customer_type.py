import requests
import json
import sys


if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]

url = f"http://{ip}:{port}/api/customers/type/"
request_data_customer_type= [
    {
        "name": "Público en General",
    },
    {
        "name": "Funcionario Policial Activo",
    },
    {
        "name": "Funcionario Policial Pasivo",
    },
    {
        "name": "Funcionario de la MUSERPOL - Miembros del Directorio",
    },
    {
        "name": "Funcionario Público",
    },
    {
        "name": "Institución Policial",
        "is_institution":"True"
    },
    {
        "name": "Institución Pública",
        "is_institution":"True"
    },
    {
        "name": "Colegio Profesional",
        "is_institution":"True"
    },
    {
        "name": "Institución Educativa",
        "is_institution":"True"
    },
    {
        "name": "Institución Deportiva",
        "is_institution":"True"
    },
    {
        "name": "Institución Cultural",
        "is_institution":"True"
    },
    {
        "name": "Otros",
        "is_institution":"True"
    }
]
for data in request_data_customer_type:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.json())