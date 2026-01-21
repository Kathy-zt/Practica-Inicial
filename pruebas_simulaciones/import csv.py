import csv
import os
import random
import time
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# =========================
# CONFIG GENERAL
# =========================
MODO = "realtime"     # "realtime" o "batch"
CSV_PATH = "ranas_parques.csv"
MEASUREMENT = "apariciones_ranas"

# 1 registro por minuto (para pruebas puedes bajar a 5s)
INTERVALO_SEGUNDOS = 60

# 10% de apariciones
PROB_APARICION = 0.10

# Si haces batch: cuántos minutos generar (ej. 24h = 1440)
BATCH_MINUTOS = 240  # ejemplo: 4 horas


# =========================
# INFLUXDB CONFIG
# =========================
URL = "http://127.0.0.1:8086"
TOKEN = "1ruSH0Pc3jda8g6QIQLbvtxqdJ6zquVnO8zwNTrCHziWWeZvT1HFIeSmDjXys5a0YCPJFYpUOxMmKFDS6R92ZA=="
ORG = "monitoreorg"
BUCKET = "monitoreo"  

# PARQUES (COORDS REALES)

PARQUES = [
    {"parque": "El Bosque",  "lat": -39.839357, "lon": -73.243782},
    {"parque": "Saval",      "lat": -39.803513, "lon": -73.258776},
    {"parque": "Kramer",     "lat": -39.834619, "lon": -73.226864},
    {"parque": "Harnecker",  "lat": -39.820556, "lon": -73.235694},
    {"parque": "Collico",    "lat": -39.818508, "lon": -73.199181},
]

DISPOSITIVOS = ["mic_01", "mic_02", "mic_03"]

RANGOS_RANAS = {
    "rana_verde": (300, 600),
    "rana_azul": (600, 900),
    "rana_roja": (900, 1200),
}

CSV_HEADERS = [
    "timestamp",
    "deviceName",
    "parque",
    "latitude",
    "longitude",
    "rana_presente",
    "tipo_rana",
    "frecuencia_hz",
    "cantidad_llamadas",
    "confianza"
]


def ensure_csv(path: str):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(CSV_HEADERS)
        print(f"[CSV] Creado: {path}")


def generar_evento(ts: datetime) -> dict:
    # elegir parque real
    p = random.choice(PARQUES)

    # decidir aparición (10%)
    rana_presente = random.random() < PROB_APARICION

    # base
    row = {
        "timestamp": ts.isoformat() + "Z",
        "deviceName": random.choice(DISPOSITIVOS),
        "parque": p["parque"],
        "latitude": p["lat"],
        "longitude": p["lon"],
        "rana_presente": rana_presente,
        "tipo_rana": "",
        "frecuencia_hz": 0.0,
        "cantidad_llamadas": 0,
        "confianza": 0.0
    }

    # si hay rana, completamos métricas
    if rana_presente:
        tipo = random.choice(list(RANGOS_RANAS.keys()))
        fmin, fmax = RANGOS_RANAS[tipo]

        row["tipo_rana"] = tipo
        row["frecuencia_hz"] = round(random.uniform(fmin, fmax), 2)
        row["cantidad_llamadas"] = random.randint(1, 10)
        row["confianza"] = round(random.uniform(0.60, 0.95), 2)

    return row


def row_to_point(row: dict) -> Point:
    # timestamp ISO Z → +00:00
    ts_str = row["timestamp"].replace("Z", "+00:00")
    ts = datetime.fromisoformat(ts_str)

    # Tags: valores categóricos (para filtrar en Grafana)
    # OJO: parque y deviceName son buenos tags (baja cardinalidad)
    p = (
        Point(MEASUREMENT)
        .time(ts)
        .tag("deviceName", row["deviceName"])
        .tag("parque", row["parque"])
        .field("latitude", float(row["latitude"]))
        .field("longitude", float(row["longitude"]))
        .field("rana_presente", 1 if row["rana_presente"] else 0)
    )

    # Si hay rana, guardamos campos relevantes
    if row["rana_presente"]:
        p = (
            p.tag("tipo_rana", row["tipo_rana"])
             .field("frecuencia_hz", float(row["frecuencia_hz"]))
             .field("cantidad_llamadas", int(row["cantidad_llamadas"]))
             .field("confianza", float(row["confianza"]))
        )
    else:
        # si NO hay rana, mantenemos valores numéricos en 0 para poder graficar conteo/presencia
        p = (
            p.field("frecuencia_hz", 0.0)
             .field("cantidad_llamadas", 0)
             .field("confianza", 0.0)
        )

    return p


def append_csv(row: dict):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        w.writerow(row)
        f.flush()


def main():
    ensure_csv(CSV_PATH)

    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(f"[Influx] URL={URL} ORG={ORG} BUCKET={BUCKET}")
    print(f"[Modo] {MODO}")

    try:
        if MODO == "realtime":
            ts = datetime.utcnow()
            print("[INFO] Tiempo real: 1 registro por minuto (Ctrl+C para detener).")
            while True:
                row = generar_evento(ts)

                # CSV + Influx inmediato
                append_csv(row)
                write_api.write(bucket=BUCKET, record=row_to_point(row))

                print(f"[OK] {row['timestamp']} parque={row['parque']} rana={row['rana_presente']} "
                      f"tipo={row['tipo_rana']} freq={row['frecuencia_hz']} calls={row['cantidad_llamadas']}")

                ts += timedelta(seconds=INTERVALO_SEGUNDOS)
                time.sleep(INTERVALO_SEGUNDOS)

        elif MODO == "batch":
            ts = datetime.utcnow()
            print(f"[INFO] Batch: generando {BATCH_MINUTOS} minutos…")
            points = []

            for _ in range(BATCH_MINUTOS):
                row = generar_evento(ts)
                append_csv(row)
                points.append(row_to_point(row))
                ts += timedelta(minutes=1)

            # escritura en bloque
            write_api.write(bucket=BUCKET, record=points)
            print(f"[OK] Batch enviado: {len(points)} registros.")

        else:
            raise ValueError("MODO inválido. Usa 'realtime' o 'batch'.")

    except KeyboardInterrupt:
        print("\n[STOP] Detenido por usuario.")
    finally:
        client.close()
        print("[Influx] Cliente cerrado.")


if __name__ == "__main__":
    main()
