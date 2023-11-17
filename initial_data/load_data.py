# main_script.py
import subprocess
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

subprocess.run(["python3", "properties_data.py", ip, port, token])
subprocess.run(["python3", "rooms_data.py", ip, port, token])