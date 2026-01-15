import csv
import time
from datetime import datetime
from typing import Dict, Any, Optional

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# =========================
# CONFIGURACIÓN INFLUXDB
# =========================
URL = "http://127.0.0.1:8086"          # mejor que localhost (evita IPv6 [::1])
TOKEN = "1ruSH0Pc3jda8g6QIQLbvtxqdJ6zquVnO8zwNTrCHziWWeZvT1HFIeSmDjXys5a0YCPJFYpUOxMmKFDS6R92ZA=="
ORG = "monitoreorg"
BUCKET = "Lectura_CSV"

# =========================
# CONFIGURACIÓN CSV
# =========================
CSV_PATH = "simulados.csv"             # o "registros.csv"
MEASUREMENT = "ranas"                  # nombre de measurement en Influx
STREAM_MODE = False                    # True = espera entre filas
STREAM_SLEEP_SECONDS = 1               # pausa si STREAM_MODE=True


# =========================
# UTILIDADES
# =========================
def parse_timestamp(value: str) -> datetime:
    """
    Soporta timestamps tipo:
    - 2025-12-26T12:00:01Z
    - 2025-12-26T12:00:01.123Z
    - 2025-12-26 12:00:01
    """
    v = value.strip()
    # Normaliza Z a formato ISO compatible
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        # último intento: formato común sin T
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def get_any(row: Dict[str, str], keys) -> Optional[str]:
    """Devuelve el primer valor existente en row para cualquiera de las keys."""
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return None


def map_row_to_point(row: Dict[str, str]) -> Point:
    """
    Mapea una fila del CSV al esquema de InfluxDB.
    Soporta nombres alternativos por si tu CSV no coincide exacto.
    Ajusta aquí si tu registros.csv tiene columnas distintas.
    """

    # --- timestamp ---
    ts_raw = get_any(row, ["timestamp", "time", "fecha", "datetime"])
    if not ts_raw:
        raise ValueError("Falta columna timestamp/time/fecha/datetime")
    ts = parse_timestamp(ts_raw)

    # --- tags (categóricos) ---
    device = get_any(row, ["device_name", "deviceName", "device", "mic", "sensor"])
    tipo_rana = get_any(row, ["tipo_rana", "rana", "species", "tipo", "class"])

    # --- fields (numéricos) ---
    lat_raw = get_any(row, ["lat", "latitude"])
    lon_raw = get_any(row, ["lon", "longitude"])
    freq_raw = get_any(row, ["frecuencia_hz", "frecuencia", "frequency_hz", "freq"])
    calls_raw = get_any(row, ["cantidad_llamadas", "llamadas", "calls", "count"])
    conf_raw = get_any(row, ["confianza", "confidence", "prob"])

    # Construye point
    p = Point(MEASUREMENT).time(ts)

    # Tags (si vienen)
    if device:
        p = p.tag("deviceName", device)
    if tipo_rana:
        p = p.tag("tipo_rana", tipo_rana)

    # Fields (solo si vienen y son válidos)
    if lat_raw is not None:
        p = p.field("latitude", float(lat_raw))
    if lon_raw is not None:
        p = p.field("longitude", float(lon_raw))
    if freq_raw is not None:
        p = p.field("frecuencia_hz", float(freq_raw))
    if calls_raw is not None:
        p = p.field("cantidad_llamadas", int(float(calls_raw)))
    if conf_raw is not None:
        p = p.field("confianza", float(conf_raw))

    return p


def main():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    ok = 0
    fail = 0

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                raise ValueError("El CSV no tiene encabezados (header).")

            print("Columnas detectadas:", reader.fieldnames)
            print(f"Escribiendo en InfluxDB → org={ORG}, bucket={BUCKET}, measurement={MEASUREMENT}")
            print("STREAM_MODE =", STREAM_MODE)

            for i, row in enumerate(reader, start=1):
                try:
                    point = map_row_to_point(row)
                    write_api.write(bucket=BUCKET, record=point)
                    ok += 1

                    if i % 50 == 0:
                        print(f"OK {ok} filas escritas...")

                    if STREAM_MODE:
                        time.sleep(STREAM_SLEEP_SECONDS)

                except Exception as e:
                    fail += 1
                    # muestra la fila y el error (sin parar todo)
                    print(f"[FILA {i}] ERROR: {e} | row={row}")

        print(f"FIN. Filas OK: {ok} | Filas con error: {fail}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
