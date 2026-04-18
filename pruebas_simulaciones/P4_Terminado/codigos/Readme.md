# Monitoreo de Anfibios con InfluxDB y Grafana

Este proyecto simula registros de avistamiento de anfibios en distintos parques, permite cargar esos datos en InfluxDB y luego visualizarlos en Grafana mediante mapas o gráficos.

---

## 1. Objetivo

El sistema permite trabajar en dos modos:

### Modo histórico
Se genera un archivo CSV con registros simulados de un día completo y luego ese archivo se sube a InfluxDB.

### Modo tiempo real
Se envían registros simulados directamente a InfluxDB cada cierto intervalo de tiempo.

Para evitar inconsistencias, todos los datos deben almacenarse en una sola estructura:

- **Bucket:** `Lectura_CSV`
- **Medición:** `monitoreo_anfibios`

---

## 2. Estructura esperada del proyecto

Se recomienda trabajar con una estructura similar a esta:

```bash
proyecto/
│
├── simulacion_historica.py
├── ingreso_csv.py
├── simulacion_tiempo_real.py
├── README.md
└── datos/
```

La carpeta `datos/` se crea automáticamente cuando se ejecuta la simulación histórica.

---

## 3. Requisitos previos

Antes de comenzar, asegúrate de tener instalado y configurado lo siguiente:

- **Python 3**
- **InfluxDB 2.x**
- **Grafana**
- La librería de Python **`influxdb-client`**

Además, en InfluxDB debes tener creado lo siguiente:

- **Organization:** `monitoreorg`
- **Bucket:** `Lectura_CSV`
- Un **token de acceso** válido

---

## 4. Instalación de dependencias

Instala la librería necesaria para conectar Python con InfluxDB:

```bash
pip install influxdb-client
```

Si en Windows el comando anterior no funciona, prueba:

```bash
python -m pip install influxdb-client
```

---

## 5. Configuración previa de InfluxDB

Antes de ejecutar los scripts, debes editar los archivos:

- `ingreso_csv.py`
- `simulacion_tiempo_real.py`

y reemplazar esta línea:

```python
INFLUX_TOKEN = "TU_TOKEN_AQUI"
```

por tu token real. Por ejemplo:

```python
INFLUX_TOKEN = "abc123_token_real"
```

También debes verificar que estos valores coincidan con tu configuración real:

```python
INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_ORG = "monitoreorg"
INFLUX_BUCKET = "Lectura_CSV"
MEDICION = "monitoreo_anfibios"
```

---

## 6. Archivos del proyecto y función de cada uno

### `simulacion_historica.py`
Genera un archivo CSV con datos simulados de un día completo.

Cada registro contiene:

- fecha y hora
- parque
- coordenadas (`lat`, `lon`)
- presencia o ausencia de anfibio
- identificadores auxiliares
- observaciones

El archivo generado se guarda dentro de la carpeta `datos/`.

### `ingreso_csv.py`
Lee el archivo CSV generado por `simulacion_historica.py` y lo sube a InfluxDB.

Los datos se almacenan en:

- **Bucket:** `Lectura_CSV`
- **Medición:** `monitoreo_anfibios`

### `simulacion_tiempo_real.py`
Genera datos simulados y los envía directamente a InfluxDB en tiempo real, sin pasar por un archivo CSV.

---

## 7. Flujo de trabajo recomendado

Existen dos formas de usar el proyecto:

### Opción A: trabajar con datos históricos
Primero se genera un archivo CSV y después se sube a InfluxDB.

### Opción B: trabajar con datos en tiempo real
Los datos se envían directamente a InfluxDB desde el script de simulación.

---

## 8. Pasos para trabajar con datos históricos

### Paso 1: generar el archivo CSV

Ejecuta:

```bash
python simulacion_historica.py 2026-04-16
```

Esto generará un archivo como el siguiente:

```bash
datos/registros_2026-04-16.csv
```

Si no indicas una fecha, el script utilizará la fecha actual del sistema.

### Paso 2: verificar que el archivo se haya creado

Revisa que el archivo exista dentro de la carpeta `datos/`.

Ejemplo esperado:

```bash
datos/registros_2026-04-16.csv
```

Si no aparece, revisa:

- si ejecutaste el script en la carpeta correcta
- si hubo un error al guardar
- la ruta exacta mostrada por el programa

### Paso 3: subir el CSV a InfluxDB

Ejecuta:

```bash
python ingreso_csv.py datos/registros_2026-04-16.csv
```

Si todo funciona bien, verás mensajes parecidos a estos:

```text
Leyendo y subiendo datos desde datos/registros_2026-04-16.csv...
1000 puntos escritos...
2000 puntos escritos...
...
Carga completa. 7200 registros subidos a InfluxDB.
```

---

## 9. Pasos para trabajar con datos en tiempo real

Ejecuta:

```bash
python simulacion_tiempo_real.py
```

Este script enviará datos continuamente a InfluxDB.

Para detenerlo, presiona:

```text
Ctrl + C
```

---

## 10. Qué datos se almacenan

Los datos se guardan en la medición:

```text
monitoreo_anfibios
```

### Tags
- `parque`
- `id_punto` (cuando los datos vienen del CSV)

### Fields
- `lat`
- `lon`
- `presencia`
- `id_rana`
- `id_usuario`
- `observaciones`

---

## 11. Advertencia importante sobre `observaciones`

El campo `observaciones` es de tipo **texto**.

Eso significa que:

- no se puede promediar
- no se puede usar con la agregación `mean`
- no debe incluirse en consultas que hagan cálculos numéricos

Si intentas hacerlo, puede aparecer un error como este:

```text
unsupported input type for mean aggregate: string
```

Ese error no significa que los datos estén mal cargados. Solo indica que InfluxDB no puede aplicar promedio a un campo de texto.

---

## 12. Cómo revisar los datos en InfluxDB Data Explorer

Para revisar correctamente los datos:

1. Abre **Data Explorer**
2. Selecciona el bucket `Lectura_CSV`
3. Selecciona la medición `monitoreo_anfibios`
4. Para consultas orientadas al mapa, utiliza solamente estos campos:
   - `lat`
   - `lon`
   - `presencia`

No uses `observaciones` si estás aplicando funciones numéricas.

---

## 13. Consulta Flux recomendada

Usa esta consulta para revisar los datos principales:

```flux
from(bucket: "Lectura_CSV")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "monitoreo_anfibios")
  |> filter(fn: (r) => r._field == "lat" or r._field == "lon" or r._field == "presencia")
```

Esta consulta es útil tanto en InfluxDB como en Grafana.

---

## 14. Configuración correcta en Grafana

### Heatmap
Usa esta configuración para visualizar intensidad de avistamientos:

- **Layer type:** `Heatmap`
- **Location mode:** `Coords`
- **Latitude field:** `lat`
- **Longitude field:** `lon`
- **Weight values:** `presencia`

Este modo sirve para mostrar zonas con mayor concentración de detecciones.

### Markers
Usa esta configuración para visualizar puntos exactos:

- **Layer type:** `Markers`
- **Location mode:** `Coords`
- **Latitude field:** `lat`
- **Longitude field:** `lon`

Este modo sirve para ver la posición puntual de cada registro.

---

## 15. Problemas comunes y solución

### Problema 1: el archivo CSV no aparece

**Posibles causas:**
- el script se ejecutó desde otra carpeta
- no se revisó la ruta correcta
- ocurrió un error al guardar

**Solución:**
- revisa la ruta mostrada por el script
- confirma que el archivo esté dentro de `datos/`
- vuelve a ejecutar el script y revisa el mensaje final

### Problema 2: error con `mean`

**Mensaje típico:**

```text
unsupported input type for mean aggregate: string
```

**Causa:**  
Se intentó aplicar `mean` a un campo de texto, como `observaciones`.

**Solución:**  
Usa solo:

- `lat`
- `lon`
- `presencia`

para consultas numéricas o visualizaciones de mapa.

### Problema 3: no aparecen datos en Grafana

**Posibles causas:**
- token incorrecto
- bucket incorrecto
- medición incorrecta
- rango de tiempo mal configurado
- consulta usando una estructura antigua o distinta

**Qué revisar:**
- bucket: `Lectura_CSV`
- medición: `monitoreo_anfibios`
- existencia de los campos `lat`, `lon`, `presencia`
- rango temporal del panel

### Problema 4: existen varias mediciones distintas

Si en InfluxDB aparecen mediciones como:

- `ranas`
- `apariciones_ranas`
- `monitoreo_anfibios`

significa que en algún momento se cargaron datos con scripts o estructuras anteriores.

**Recomendación final:**  
Trabajar solo con la medición:

```text
monitoreo_anfibios
```

para mantener consistencia en las consultas y paneles.

---

## 16. Comandos resumidos

### Generar CSV histórico

```bash
python simulacion_historica.py 2026-04-16
```

### Subir CSV a InfluxDB

```bash
python ingreso_csv.py datos/registros_2026-04-16.csv
```

### Ejecutar simulación en tiempo real

```bash
python simulacion_tiempo_real.py
```
