import time
import random
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "OY3nJx5Wjh78rJegdfnQ2FXTQ0EFP3bo1yOmDx5H3aRsvSikAyTEVrkujX4NCv0cd26ibi6z2bFWOLZ52U05ig=="
INFLUX_ORG = "monitoreorg"
INFLUX_BUCKET = "Lectura_CSV"

PARQUES = {
    "El Bosque":  (-39.839357, -73.243782),
    "Saval":      (-39.803513, -73.258776),
    "Kramer":     (-39.834619, -73.226864),
    "Harnecker":  (-39.820556, -73.235694),
    "Collico":    (-39.818508, -73.199181),
}

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

print("Iniciando tiempo real (1 muestra/min)...")
try: #se conecta a InfluxDB y simula datos cada minuto para cada parque, con una probabilidad del 10% de detectar una rana. Se detiene con Ctrl+C.
    while True:
        ts = datetime.utcnow()
        for nombre, (lat_base, lon_base) in PARQUES.items():
            lat = lat_base + random.uniform(-0.0005, 0.0005)
            lon = lon_base + random.uniform(-0.0005, 0.0005)
            rana = 1 if random.random() < 0.10 else 0
            
            p = Point("monitoreo_anfibios") \
                .tag("parque", nombre) \
                .field("lat", lat) \
                .field("lon", lon) \
                .field("presencia", rana) \
                .time(ts)
            
            write_api.write(bucket=INFLUX_BUCKET, record=p)
            
        print(f"[{ts}] Datos enviados para todos los parques.")
        time.sleep(60) # Esperar 1 minuto
except KeyboardInterrupt:
    client.close()
print("Simulación detenida por el usuario.") 
