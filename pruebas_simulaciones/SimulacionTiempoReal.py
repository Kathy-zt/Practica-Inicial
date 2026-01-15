import csv
import os
import random
import time
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# =========================
# CONFIG INFLUXDB (AJUSTA)
# =========================
URL = "http://127.0.0.1:8086"
TOKEN = "1ruSH0Pc3jda8g6QIQLbvtxqdJ6zquVnO8zwNTrCHziWWeZvT1HFIeSmDjXys5a0YCPJFYpUOxMmKFDS6R92ZA=="
ORG = "monitoreorg"          # ajusta si tu org se llama distinto
BUCKET = "Lectura_CSV"         # tu bucket (confirmado)

MEASUREMENT = "ranas"

# =========================
# CONFIG CSV
# =========================
CSV_PATH = "stream_ranas.csv"

# Columnas del CSV (esquema)
CSV_HEADERS = [
    "timestamp",
    "deviceName",
    "latitude",
    "longitude",
    "tipo_rana",
    "frecuencia_hz",
    "cantidad_llamadas",
    "confianza"
]

# =========================
# SIMULACIÓN (AJUSTABLE)
# =========================
INTERVALO_SEGUNDOS = 2  # cada cuánto se genera y envía un registro

DISPOSITIVOS = ["mic_01", "mic_02"]
RANGOS_RANAS = {
    "rana_verde": (300, 600),
    "rana_azul": (600, 900),
    "rana_roja": (900, 1200),
}

LAT_BASE = -39.80
LON_BASE = -73.20


def ensure_csv_with_header(path: str, headers: list[str]) -> None:
    """
    Crea el CSV con header si no existe.
    Si existe, no lo pisa.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
        print(f"[CSV] Creado con header: {path}")


def generate_row(ts: datetime) -> dict:
    """
    Genera una fila coherente con la simulación bioacústica.
    """
    tipo = random.choice(list(RANGOS_RANAS.keys()))
    fmin, fmax = RANGOS_RANAS[tipo]

    return {
        "timestamp": ts.isoformat() + "Z",
        "deviceName": random.choice(DISPOSITIVOS),
        "latitude": round(LAT_BASE + random.uniform(-0.01, 0.01), 6),
        "longitude": round(LON_BASE + random.uniform(-0.01, 0.01), 6),
        "tipo_rana": tipo,
        "frecuencia_hz": round(random.uniform(fmin, fmax), 2),
        "cantidad_llamadas": random.randint(1, 10),
        "confianza": round(random.uniform(0.60, 0.95), 2),
    }


def row_to_point(row: dict) -> Point:
    """
    Convierte una fila a un Point para InfluxDB.
    Recomendación: tags para filtros (deviceName, tipo_rana),
    fields para valores numéricos.
    """
    # timestamp
    # (InfluxDB acepta RFC3339 como string con Z)
    ts_str = row["timestamp"].replace("Z", "+00:00")
    ts = datetime.fromisoformat(ts_str)

    p = (
        Point(MEASUREMENT)
        .time(ts)
        .tag("deviceName", row["deviceName"])
        .tag("tipo_rana", row["tipo_rana"])
        .field("latitude", float(row["latitude"]))
        .field("longitude", float(row["longitude"]))
        .field("frecuencia_hz", float(row["frecuencia_hz"]))
        .field("cantidad_llamadas", int(row["cantidad_llamadas"]))
        .field("confianza", float(row["confianza"]))
    )
    return p


def main():
    ensure_csv_with_header(CSV_PATH, CSV_HEADERS)

    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(f"[Influx] URL={URL} ORG={ORG} BUCKET={BUCKET} MEASUREMENT={MEASUREMENT}")
    print("[INFO] Enviando datos en tiempo real. Ctrl+C para detener.\n")

    try:
        ts = datetime.utcnow()
        while True:
            row = generate_row(ts)

            # 1) append al CSV
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                w.writerow(row)
                f.flush()  # fuerza escritura a disco

            # 2) escribir a Influx inmediatamente
            point = row_to_point(row)
            write_api.write(bucket=BUCKET, record=point)

            print(f"[OK] {row['timestamp']} {row['deviceName']} {row['tipo_rana']} "
                  f"freq={row['frecuencia_hz']}Hz calls={row['cantidad_llamadas']} conf={row['confianza']}")

            ts += timedelta(seconds=INTERVALO_SEGUNDOS)
            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\n[STOP] Detenido por usuario (Ctrl+C).")
    finally:
        client.close()
        print("[Influx] Cliente cerrado.")


if __name__ == "__main__":
    main()
