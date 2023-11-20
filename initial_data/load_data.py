import subprocess
import sys
import requests
import json

if len(sys.argv) < 2:
    print("Debes proporcionar IP, puerto como argumentos.")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
url = f"http://{ip}:{port}/api/login/auth/"
username = input("introduzca su username: ")
password = input("introduzca su contraseña: ")
response = requests.post(url, data={"username": username, "password":password})
try:
    response.raise_for_status()
    response_json = response.json()
    if response.status_code == 200:
        token= response_json['access']
        subprocess.run(["python3", "properties_data.py", ip, port, token])
        subprocess.run(["python3", "rooms_data.py", ip, port, token])
        subprocess.run(["python3", "sub_enviroment_data.py",ip, port, token])
        subprocess.run(["python3", "hour_range_data.py",ip, port, token])
    else:
        error_message = response_json.get('error', 'Error desconocido')
        print(f"Error en la solicitud HTTP: {response.status_code}")
        print(f"Mensaje de error: {error_message}")
except requests.exceptions.HTTPError as err:
    print(f"Error en la solicitud HTTP: {err}")
    try:
        error_response_json = err.response.json()
        error_message = error_response_json.get('error', 'Detalles de error no disponibles')
        print(f"Mensaje de error: {error_message}")
    except json.decoder.JSONDecodeError:
        print("La respuesta del servidor no es un JSON válido.")
    sys.exit(1)
except json.decoder.JSONDecodeError:
    print("La respuesta del servidor no es un JSON válido.")
    sys.exit(1)
