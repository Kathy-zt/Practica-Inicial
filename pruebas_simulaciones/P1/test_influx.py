import random
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS # Importar opción de escritura síncrona
##Comienza la configuración del cliente InfluxDB
url = "http://localhost:8086"
token = "5H1aQrdMbl_b_t7cB6fDnBk3LdoPKGB-9ccHrgkeg_YyOt_2rzDkekpbfqbv6D07My7zwRSFsRMufj931_pCXQ=="
org = "monitoreorg"
bucket = "monitoreo"

# Crear el cliente InfluxDB para interactuar con la base de datos
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

ranas = {
    "rana_verde": (300, 600),
    "rana_azul": (600, 900),
    "rana_roja": (900, 1200),
}

devices = {
    "mic_01": (-39.800, -73.200),
    "mic_02": (-39.802, -73.198),
}

intervalo = 10

print("Simulación bioacústica estable (Ctrl+C para detener)")

try:
    while True:
        for device, (lat_base, lon_base) in devices.items():
            for tipo, (fmin, fmax) in ranas.items():

                point = (
                    Point("ranas")
                    .tag("tipo", tipo)
                    .tag("deviceName", device)
                    .field("frecuencia", random.uniform(fmin, fmax))
                    .field("cantidad_llamadas", random.randint(0, 20))
                    .field("latitude", lat_base + random.uniform(-0.001, 0.001))
                    .field("longitude", lon_base + random.uniform(-0.001, 0.001))
                )

                write_api.write(bucket=bucket, record=point)

                print(f"{device} | {tipo}")

        time.sleep(intervalo)

except KeyboardInterrupt:
    print("\nDeteniendo simulación...")

finally:
    client.close()
    print("Cliente InfluxDB cerrado correctamente")
