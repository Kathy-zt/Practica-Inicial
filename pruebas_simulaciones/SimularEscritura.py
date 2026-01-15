import csv
import random
from datetime import datetime, timedelta

# ===============================
# CONFIGURACIÓN
# ===============================
ARCHIVO = "simulados.csv"# esta linea define el nombre del archivo csv
NUM_REGISTROS = 100
INTERVALO_SEGUNDOS = 10

DISPOSITIVOS = ["mic_01", "mic_02"]
RANGOS_RANAS = {
    "rana_verde": (300, 600),
    "rana_azul": (600, 900),
    "rana_roja": (900, 1200)
}

LAT_BASE = -39.8
LON_BASE = -73.2

# ===============================
# ESCRITURA CSV, 
# ===============================
with open(ARCHIVO, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # Header esto es para la cabecera del csv, lo que significa cada columna
    writer.writerow([
        "timestamp",
        "device_name",
        "lat",
        "lon",
        "tipo_rana",
        "frecuencia_hz",
        "cantidad_llamadas",
        "confianza"
    ])

    tiempo_actual = datetime.utcnow()
# este for sera para generar los registros 

    for _ in range(NUM_REGISTROS):
        tipo_rana = random.choice(list(RANGOS_RANAS.keys()))
        freq_min, freq_max = RANGOS_RANAS[tipo_rana]

        fila = [
            tiempo_actual.isoformat() + "Z",
            random.choice(DISPOSITIVOS),
            round(LAT_BASE + random.uniform(-0.01, 0.01), 6),
            round(LON_BASE + random.uniform(-0.01, 0.01), 6),
            tipo_rana,
            round(random.uniform(freq_min, freq_max), 2),
            random.randint(1, 10),
            round(random.uniform(0.6, 0.95), 2)
        ]

        writer.writerow(fila)
        tiempo_actual += timedelta(seconds=INTERVALO_SEGUNDOS)

print(f"CSV '{ARCHIVO}' generado con {NUM_REGISTROS} registros.")
