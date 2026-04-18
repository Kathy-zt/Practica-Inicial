import sys
import csv
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_TOKEN = "OY3nJx5Wjh78rJegdfnQ2FXTQ0EFP3bo1yOmDx5H3aRsvSikAyTEVrkujX4NCv0cd26ibi6z2bFWOLZ52U05ig=="
INFLUX_ORG = "monitoreorg"
INFLUX_BUCKET = "Lectura_CSV"
MEDICION = "monitoreo_anfibios"

if len(sys.argv) < 2:
    print("Uso: python ingreso_csv.py datos/registros_2026-04-16.csv")
    sys.exit(1)

archivo = sys.argv[1]

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

print(f"Leyendo y subiendo datos desde {archivo}...")

puntos = []
total = 0

try:
    with open(archivo, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            ts = datetime.strptime(row["fecha_hora"], "%Y-%m-%d %H:%M:%S")

            punto = (
                Point(MEDICION)
                .tag("parque", row["parque"])
                .tag("id_punto", str(row["id_punto"]))
                .field("lat", float(row["lat"]))
                .field("lon", float(row["lon"]))
                .field("presencia", int(row["presencia"]))
                .field("id_rana", int(row["id_rana"]))
                .field("id_usuario", int(row["id_usuario"]))
                .field("observaciones", row["observaciones"])
                .time(ts)
            )

            puntos.append(punto)
            total += 1

            if len(puntos) >= 1000:
                write_api.write(bucket=INFLUX_BUCKET, record=puntos)
                puntos = []
                print(f"{total} puntos escritos...")

    if puntos:
        write_api.write(bucket=INFLUX_BUCKET, record=puntos)

    print(f"Carga completa. {total} registros subidos a InfluxDB.")

except Exception as e:
    print("Error al subir el CSV:")
    print(e)

finally:
    client.close()