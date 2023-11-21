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
url = f"http://{ip}:{port}/api/product/"
script_directory = os.path.dirname(os.path.realpath(__file__))
media_directory = os.path.join(script_directory, "..", "media")
requests_data = [
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 1,
        "hour_range": 1,
        "mount": 3500
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 1,
        "hour_range": 2,
        "mount": 2250
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 1,
        "hour_range": 1,
        "mount": 3220
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 1,
        "hour_range": 2,
        "mount": 2070
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 1,
        "hour_range": 1,
        "mount": 2800
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 1,
        "hour_range": 2,
        "mount": 1800
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 1,
        "hour_range": 1,
        "mount": 3500
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 1,
        "hour_range": 2,
        "mount": 1690
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 1,
        "hour_range": 1,
        "mount": 2415
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 1,
        "hour_range": 2,
        "mount": 1555
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 1,
        "hour_range": 1,
        "mount": 2100
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 1,
        "hour_range": 2,
        "mount": 1350
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 1,
        "hour_range": 1,
        "mount": 3150
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 1,
        "hour_range": 2,
        "mount": 2025
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 1,
        "hour_range": 1,
        "mount": 2898
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 1,
        "hour_range": 2,
        "mount": 1863
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 1,
        "hour_range": 1,
        "mount": 2520
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 1,
        "hour_range": 2,
        "mount": 1620
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 1,
        "hour_range": 1,
        "mount": 1840
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 1,
        "hour_range": 2,
        "mount": 1183
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 1,
        "hour_range": 1,
        "mount": 1695
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 1,
        "hour_range": 2,
        "mount": 1090
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 1,
        "hour_range": 1,
        "mount": 1470
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 1,
        "hour_range": 2,
        "mount": 945
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 1,
        "hour_range": 1,
        "mount": 2450
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 1,
        "hour_range": 2,
        "mount": 1575
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 1,
        "hour_range": 1,
        "mount": 2254
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 1,
        "hour_range": 2,
        "mount": 1449
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 1,
        "hour_range": 1,
        "mount": 1960
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 1,
        "hour_range": 2,
        "mount": 1260
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 1,
        "hour_range": 1,
        "mount": 2800
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 1,
        "hour_range": 2,
        "mount": 1800
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 1,
        "hour_range": 1,
        "mount": 2576
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 1,
        "hour_range": 2,
        "mount": 1656
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 1,
        "hour_range": 1,
        "mount": 2240
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 1,
        "hour_range": 2,
        "mount": 1440
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 2,
        "hour_range": 1,
        "mount": 1750
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 2,
        "hour_range": 2,
        "mount": 1000
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 2,
        "hour_range": 1,
        "mount": 1610
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 2,
        "hour_range": 2,
        "mount": 920
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 2,
        "hour_range": 1,
        "mount": 1400
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 2,
        "hour_range": 2,
        "mount": 800
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 2,
        "hour_range": 1,
        "mount": 1315
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 2,
        "hour_range": 2,
        "mount": 750
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 2,
        "hour_range": 1,
        "mount": 1210
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 2,
        "hour_range": 2,
        "mount": 690
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 2,
        "hour_range": 1,
        "mount": 1050
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 2,
        "hour_range": 2,
        "mount": 600
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 2,
        "hour_range": 1,
        "mount": 1575
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 2,
        "hour_range": 2,
        "mount": 900
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 2,
        "hour_range": 1,
        "mount": 1449
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 2,
        "hour_range": 2,
        "mount": 828
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 2,
        "hour_range": 1,
        "mount": 1260
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 2,
        "hour_range": 2,
        "mount": 720
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 2,
        "hour_range": 1,
        "mount": 925
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 2,
        "hour_range": 2,
        "mount": 525
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 2,
        "hour_range": 1,
        "mount": 847
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 2,
        "hour_range": 2,
        "mount": 483
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 2,
        "hour_range": 1,
        "mount": 735
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 2,
        "hour_range": 2,
        "mount": 420
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 2,
        "hour_range": 1,
        "mount": 1225
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 2,
        "hour_range": 2,
        "mount": 700
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 2,
        "hour_range": 1,
        "mount": 1127
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 2,
        "hour_range": 2,
        "mount": 644
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 2,
        "hour_range": 1,
        "mount": 980
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 2,
        "hour_range": 2,
        "mount": 560
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 2,
        "hour_range": 1,
        "mount": 1400
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 2,
        "hour_range": 2,
        "mount": 800
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 2,
        "hour_range": 1,
        "mount": 1288
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 2,
        "hour_range": 2,
        "mount": 736
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 2,
        "hour_range": 1,
        "mount": 1120
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 2,
        "hour_range": 2,
        "mount": 640
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 3,
        "hour_range": 1,
        "mount": 875
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 3,
        "hour_range": 2,
        "mount": 500
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 3,
        "hour_range": 1,
        "mount": 805
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 3,
        "hour_range": 2,
        "mount": 460
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 3,
        "hour_range": 1,
        "mount": 700
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 3,
        "hour_range": 2,
        "mount": 400
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 3,
        "hour_range": 1,
        "mount": 660
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 3,
        "hour_range": 2,
        "mount": 375
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 3,
        "hour_range": 1,
        "mount": 605
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 3,
        "hour_range": 2,
        "mount": 345
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 3,
        "hour_range": 1,
        "mount": 525
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 3,
        "hour_range": 2,
        "mount": 300
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 3,
        "hour_range": 1,
        "mount": 790
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 3,
        "hour_range": 2,
        "mount": 450
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 3,
        "hour_range": 1,
        "mount": 725
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 3,
        "hour_range": 2,
        "mount": 414
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 3,
        "hour_range": 1,
        "mount": 630
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 3,
        "hour_range": 2,
        "mount": 360
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 3,
        "hour_range": 1,
        "mount": 462
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 3,
        "hour_range": 2,
        "mount": 265
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 3,
        "hour_range": 1,
        "mount": 425
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 3,
        "hour_range": 2,
        "mount": 245
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 3,
        "hour_range": 1,
        "mount": 370
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 3,
        "hour_range": 2,
        "mount": 210
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 3,
        "hour_range": 1,
        "mount": 615
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 3,
        "hour_range": 2,
        "mount": 350
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 3,
        "hour_range": 1,
        "mount": 565
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 3,
        "hour_range": 2,
        "mount": 322
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 3,
        "hour_range": 1,
        "mount": 490
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 3,
        "hour_range": 2,
        "mount": 280
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 3,
        "hour_range": 1,
        "mount": 700
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 3,
        "hour_range": 2,
        "mount": 400
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 3,
        "hour_range": 1,
        "mount": 644
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 3,
        "hour_range": 2,
        "mount": 368
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 3,
        "hour_range": 1,
        "mount": 560
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 3,
        "hour_range": 2,
        "mount": 320
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 4,
        "hour_range": 1,
        "mount": 1875
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 4,
        "hour_range": 1,
        "mount": 1725
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 4,
        "hour_range": 1,
        "mount": 1500
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 4,
        "hour_range": 1,
        "mount": 1410
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 4,
        "hour_range": 1,
        "mount": 1295
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 4,
        "hour_range": 1,
        "mount": 1125
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 4,
        "hour_range": 1,
        "mount": 1690
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 4,
        "hour_range": 1,
        "mount": 1555
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 4,
        "hour_range": 1,
        "mount": 1350
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 4,
        "hour_range": 1,
        "mount": 987
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 4,
        "hour_range": 1,
        "mount": 910
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 4,
        "hour_range": 1,
        "mount": 790
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 4,
        "hour_range": 1,
        "mount": 1315
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 4,
        "hour_range": 1,
        "mount": 1210
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 4,
        "hour_range": 1,
        "mount": 1050
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 4,
        "hour_range": 1,
        "mount": 1500
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 4,
        "hour_range": 1,
        "mount": 1380
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 4,
        "hour_range": 1,
        "mount": 1200
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 5,
        "hour_range": 1,
        "mount": 3000
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 5,
        "hour_range": 2,
        "mount": 2000
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 5,
        "hour_range": 1,
        "mount": 2800
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 5,
        "hour_range": 2,
        "mount": 1700
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 5,
        "hour_range": 1,
        "mount": 2520
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 5,
        "hour_range": 2,
        "mount": 1530
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 5,
        "hour_range": 1,
        "mount": 2250
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 5,
        "hour_range": 2,
        "mount": 1500
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 5,
        "hour_range": 1,
        "mount": 2100
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 5,
        "hour_range": 2,
        "mount": 1275
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 5,
        "hour_range": 1,
        "mount": 1890
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 5,
        "hour_range": 2,
        "mount": 1150
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 5,
        "hour_range": 1,
        "mount": 2700
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 5,
        "hour_range": 2,
        "mount": 1800
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 5,
        "hour_range": 1,
        "mount": 2520
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 5,
        "hour_range": 2,
        "mount": 1530
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 5,
        "hour_range": 1,
        "mount": 2168
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 5,
        "hour_range": 2,
        "mount": 1377
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 5,
        "hour_range": 1,
        "mount": 1575
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 5,
        "hour_range": 2,
        "mount": 1050
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 5,
        "hour_range": 1,
        "mount": 1470
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 5,
        "hour_range": 2,
        "mount": 895
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 5,
        "hour_range": 1,
        "mount": 1323
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 5,
        "hour_range": 2,
        "mount": 805
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 5,
        "hour_range": 1,
        "mount": 2100
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 5,
        "hour_range": 2,
        "mount": 1400
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 5,
        "hour_range": 1,
        "mount": 1960
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 5,
        "hour_range": 2,
        "mount": 1190
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 5,
        "hour_range": 1,
        "mount": 1764
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 5,
        "hour_range": 2,
        "mount": 1071
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 5,
        "hour_range": 1,
        "mount": 2400
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 5,
        "hour_range": 2,
        "mount": 1600
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 5,
        "hour_range": 1,
        "mount": 2240
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 5,
        "hour_range": 2,
        "mount": 1360
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 5,
        "hour_range": 1,
        "mount": 2016
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 5,
        "hour_range": 2,
        "mount": 1224
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 6,
        "hour_range": 1,
        "mount": 2200
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 6,
        "hour_range": 2,
        "mount": 1500
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 6,
        "hour_range": 1,
        "mount": 2000
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 6,
        "hour_range": 2,
        "mount": 1300
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 6,
        "hour_range": 1,
        "mount": 1800
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 6,
        "hour_range": 2,
        "mount": 1170
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 6,
        "hour_range": 1,
        "mount": 1650
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 6,
        "hour_range": 2,
        "mount": 1125
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 6,
        "hour_range": 1,
        "mount": 1500
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 6,
        "hour_range": 2,
        "mount": 975
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 6,
        "hour_range": 1,
        "mount": 1350
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 6,
        "hour_range": 2,
        "mount": 880
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 6,
        "hour_range": 1,
        "mount": 1980
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 6,
        "hour_range": 2,
        "mount": 1350
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 6,
        "hour_range": 1,
        "mount": 1800
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 6,
        "hour_range": 2,
        "mount": 1170
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 6,
        "hour_range": 1,
        "mount": 1620
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 6,
        "hour_range": 2,
        "mount": 1053
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 6,
        "hour_range": 1,
        "mount": 1155
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 6,
        "hour_range": 2,
        "mount": 790
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 6,
        "hour_range": 1,
        "mount": 1050
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 6,
        "hour_range": 2,
        "mount": 685
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 6,
        "hour_range": 1,
        "mount": 945
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 6,
        "hour_range": 2,
        "mount": 616
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 6,
        "hour_range": 1,
        "mount": 1540
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 6,
        "hour_range": 2,
        "mount": 1050
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 6,
        "hour_range": 1,
        "mount": 1400
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 6,
        "hour_range": 2,
        "mount": 910
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 6,
        "hour_range": 1,
        "mount": 1260
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 6,
        "hour_range": 2,
        "mount": 819
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 6,
        "hour_range": 1,
        "mount": 1760
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 6,
        "hour_range": 2,
        "mount": 1200
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 6,
        "hour_range": 1,
        "mount": 1600
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 6,
        "hour_range": 2,
        "mount": 1040
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 6,
        "hour_range": 1,
        "mount": 1440
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 6,
        "hour_range": 2,
        "mount": 936
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 7,
        "hour_range": 1,
        "mount": 4900
    },
    {
        "day": ["SÁBADO"],
        "rate": 1,
        "room": 7,
        "hour_range": 2,
        "mount": 3000
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 7,
        "hour_range": 1,
        "mount": 4500
    },
    {
        "day": ["VIERNES"],
        "rate": 1,
        "room": 7,
        "hour_range": 2,
        "mount": 2700
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 7,
        "hour_range": 1,
        "mount": 4050
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 1,
        "room": 7,
        "hour_range": 2,
        "mount": 2430
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 7,
        "hour_range": 1,
        "mount": 3675
    },
    {
        "day": ["SÁBADO"],
        "rate": 2,
        "room": 7,
        "hour_range": 2,
        "mount": 2250
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 7,
        "hour_range": 1,
        "mount": 3375
    },
    {
        "day": ["VIERNES"],
        "rate": 2,
        "room": 7,
        "hour_range": 2,
        "mount": 2025
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 7,
        "hour_range": 1,
        "mount": 3040
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 2,
        "room": 7,
        "hour_range": 2,
        "mount": 1825
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 7,
        "hour_range": 1,
        "mount": 4410
    },
    {
        "day": ["SÁBADO"],
        "rate": 3,
        "room": 7,
        "hour_range": 2,
        "mount": 2700
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 7,
        "hour_range": 1,
        "mount": 4050
    },
    {
        "day": ["VIERNES"],
        "rate": 3,
        "room": 7,
        "hour_range": 2,
        "mount": 2430
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 7,
        "hour_range": 1,
        "mount": 3645
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 3,
        "room": 7,
        "hour_range": 2,
        "mount": 2187
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 7,
        "hour_range": 1,
        "mount": 2575
    },
    {
        "day": ["SÁBADO"],
        "rate": 4,
        "room": 7,
        "hour_range": 2,
        "mount": 1575
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 7,
        "hour_range": 1,
        "mount": 2365
    },
    {
        "day": ["VIERNES"],
        "rate": 4,
        "room": 7,
        "hour_range": 2,
        "mount": 1420
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 7,
        "hour_range": 1,
        "mount": 2128
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 4,
        "room": 7,
        "hour_range": 2,
        "mount": 1280
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 7,
        "hour_range": 1,
        "mount": 3430
    },
    {
        "day": ["SÁBADO"],
        "rate": 5,
        "room": 7,
        "hour_range": 2,
        "mount": 2100
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 7,
        "hour_range": 1,
        "mount": 3150
    },
    {
        "day": ["VIERNES"],
        "rate": 5,
        "room": 7,
        "hour_range": 2,
        "mount": 1890
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 7,
        "hour_range": 1,
        "mount": 2835
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 5,
        "room": 7,
        "hour_range": 2,
        "mount": 1701
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 7,
        "hour_range": 1,
        "mount": 3920
    },
    {
        "day": ["SÁBADO"],
        "rate": 6,
        "room": 7,
        "hour_range": 2,
        "mount": 2400
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 7,
        "hour_range": 1,
        "mount": 3600
    },
    {
        "day": ["VIERNES"],
        "rate": 6,
        "room": 7,
        "hour_range": 2,
        "mount": 2160
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 7,
        "hour_range": 1,
        "mount": 3240
    },
    {
        "day": ["DOMINGO","LUNES","MARTES","MIÉRCOLES","JUEVES"],
        "rate": 6,
        "room": 7,
        "hour_range": 2,
        "mount": 1944
    }
]
for data in requests_data:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, data={"day": data["day"], "rate":data["rate"],"room":data["room"],"hour_range":data["hour_range"],"mount":data["mount"]}, headers=headers)
    print(response.status_code, response.json())