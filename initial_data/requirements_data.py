import requests
import json
import sys


if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]

url = f"http://{ip}:{port}/api/requirements/"

request_data_requirements = [
    {
        "requirement_name":"FOTOCOPIA C.I."
    },
    {
        "requirement_name":"FORMULARIO DE RESERVA EFECTIVA"
    },
    {
        "requirement_name":"BENEFICIARIO SIGEP"
    },
    {
        "requirement_name":"BOLETA DE PAGO"
    },
    {
        "requirement_name":"RESOLUCIÓN O MEMORANDUM DESIG"
    },
    {
        "requirement_name":"FOTOCOPIA MATRICULA DE COMERCIO-PERSONA JURÍDICA"
    },
    {
        "requirement_name":"FOTOCOPIA DE PODER DEL REPRESENTANTE LEGAL-PERSONA JURÍDICA"
    },
    {
        "requirement_name":"FOTOCOPIA DE CI. DE REPRESENTANTE LEGAL"
    },
    {
        "requirement_name":"SOLICITUD DE ALQUILER"
    },
]
for data in request_data_requirements:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.json())