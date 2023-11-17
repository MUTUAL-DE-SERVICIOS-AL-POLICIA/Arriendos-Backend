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
url = f"http://{ip}:{port}/api/rooms/properties/"
script_directory = os.path.dirname(os.path.realpath(__file__))
media_directory = os.path.join(script_directory, "..", "media")

requests_data = [
    {
        "name": "GRAN HOTEL PARIS",
        "address":"La Paz",
        "photo": ("GRAN_HOTEL_PARIS.jpeg", open(os.path.join(media_directory, "property_photos/GRAN_HOTEL_PARIS.jpeg"), "rb")),
    },
    {
        "name": "CLUB POLICIAL LOS OLIVOS",
        "photo": ("CLUB_POLICIAL_LOS_OLIVOS.jpg", open(os.path.join(media_directory, "property_photos/CLUB_POLICIAL_LOS_OLIVOS.jpg"), "rb")),
        "address": "La Paz"
    }
]

for data in requests_data:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, data={"name": data["name"],"address":data["address"]}, files={"photo": data["photo"]}, headers=headers)
    print(response.status_code, response.json())
