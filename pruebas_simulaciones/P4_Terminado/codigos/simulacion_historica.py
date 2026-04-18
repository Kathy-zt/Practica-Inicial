import csv
import random
import sys
import os
from datetime import datetime, timedelta

PARQUES = {
    1: {"nombre": "El Bosque", "lat": -39.839357, "lon": -73.243782},
    2: {"nombre": "Saval", "lat": -39.803513, "lon": -73.258776},
    3: {"nombre": "Kramer", "lat": -39.834619, "lon": -73.226864},
    4: {"nombre": "Harnecker", "lat": -39.820556, "lon": -73.235694},
    5: {"nombre": "Collico", "lat": -39.818508, "lon": -73.199181},
}

PROB_RANA = 0.10
REGISTROS_POR_DIA = 1440  # 1 por minuto

fecha_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")

try:
    fecha_base = datetime.strptime(fecha_str, "%Y-%m-%d")
except ValueError:
    print("Formato de fecha incorrecto. Usa AAAA-MM-DD.")
    sys.exit(1)

carpeta_salida = "datos"
os.makedirs(carpeta_salida, exist_ok=True)

archivo_salida = os.path.join(carpeta_salida, f"registros_{fecha_str}.csv")
ruta_completa = os.path.abspath(archivo_salida)

print(f"Generando datos simulados para la fecha: {fecha_str}...")
print(f"Se guardará en: {ruta_completa}")

try:
    with open(archivo_salida, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "fecha_hora",
            "id_punto",
            "parque",
            "lat",
            "lon",
            "presencia",
            "id_rana",
            "id_usuario",
            "observaciones",
        ])

        total = 0

        for minuto in range(REGISTROS_POR_DIA):
            tiempo_actual = fecha_base + timedelta(minutes=minuto)

            for id_punto, info in PARQUES.items():
                lat = info["lat"] + random.uniform(-0.002, 0.002)
                lon = info["lon"] + random.uniform(-0.002, 0.002)

                presencia = 1 if random.random() < PROB_RANA else 0
                id_rana = random.randint(1, 5) if presencia else 0
                id_usuario = random.randint(1, 3)

                if presencia:
                    observaciones = random.choice([
                        "Vocalización",
                        "Múltiples individuos",
                        "Ejemplar adulto"
                    ])
                else:
                    observaciones = "Sin avistamiento"

                writer.writerow([
                    tiempo_actual.strftime("%Y-%m-%d %H:%M:%S"),
                    id_punto,
                    info["nombre"],
                    f"{lat:.6f}",
                    f"{lon:.6f}",
                    presencia,
                    id_rana,
                    id_usuario,
                    observaciones
                ])
                total += 1

    print("Archivo generado correctamente.")
    print(f"Total de registros guardados: {total}")

except Exception as e:
    print("Ocurrió un error al guardar el archivo:")
    print(e)