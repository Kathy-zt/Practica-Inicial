import random
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
url = "http://localhost:8086"
token = "nEijLzyd4XwcKiQ-dUV-QbJhgst3wu9NVwV4LLFQta-vST3utkxV6bJ_1WYxBjpMTgVH4b-RSqPrO2wPiE8cDA=="
org = "monitoreo_org"
bucket = "monitoreo_bucket"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Tipos de ranitas
tipos_ranitas = ["verde", "azul", "roja"]

print("Monitoreo de ranitas iniciado (Ctrl+C para detener)")

# -----------------------------
# BUCLE DE MONITOREO
# -----------------------------
while True:
    for tipo in tipos_ranitas:
        cantidad = random.randint(0, 5)

        point = (
            Point("ranitas")
            .tag("tipo", tipo)
            .field("cantidad", cantidad)
        )

        write_api.write(bucket=bucket, record=point)

        print(f"Tipo: {tipo} | Cantidad: {cantidad}")

    time.sleep(10)  # cada 10 segundos
