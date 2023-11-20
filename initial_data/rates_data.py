import requests
import json
import sys


if len(sys.argv) < 4:
    print("Debes proporcionar IP, puerto, URL y token como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
token = sys.argv[3]

url = f"http://{ip}:{port}/api/requirements/rates/"

request_data_rates= [
    {
        "rate":"Tarifa regular",
        "requirement":[1,2,3],
        "customer_type":[1]
    },
    {
        "rate":"Tarifa preferencial",
        "requirement":[1,2,3,4],
        "customer_type":[2,3,4]
    },
    {
        "rate":"Tarifa funcionario público",
        "requirement":[1,2,3,4],
        "customer_type":[5]
    },
    {
        "rate":"Tarifa promocional instituciones policiales",
        "requirement":[1,2,3,4,5],
        "customer_type":[6]
    },
    {
        "rate":"Tarifa promocional Instituciones públicas",
        "requirement":[1,2,3,4,5],
        "customer_type":[7]
    },
    {
        "rate":"Tarifa promocional educativos, culturales, deportivas y otros",
        "requirement":[1,2,3,4,5],
        "customer_type":[8,9,10,11,12]
    }
]
for data in request_data_rates:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.json())
