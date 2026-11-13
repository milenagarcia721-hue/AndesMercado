# AndesMercado — Calidad de datos con DevOps

Proyecto académico para impedir que ventas con unidades incorrectas lleguen al Data Warehouse y a Power BI.

## Estructura

- `validar_ventas.py`: reglas de calidad y CLI con código de salida 1 si hay incumplimientos.
- `tests/test_validar_ventas.py`: pruebas unitarias con `pytest`.
- `ventas.csv`: conjunto corregido que debe pasar el CI.
- `ventas_anexo.csv`: conjunto original del caso; debe fallar por el incidente.
- `.github/workflows/ci.yml`: GitHub Actions en cada push y pull request. También permite ejecutar manualmente cualquiera de los dos CSV.

## Requisitos

Python 3.10 o superior. Se recomienda Python 3.12.

## Ejecución local

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pytest -v
python validar_ventas.py ventas.csv
```

Resultado esperado: las pruebas pasan y `ventas.csv` muestra `VALIDACIÓN EXITOSA`.

## Reproducir el bloqueo del incidente

```bash
python validar_ventas.py ventas_anexo.csv
```

Resultado esperado: el proceso termina con código 1 y reporta ventas individuales por encima de COP 5.000.000 y un total diario anómalo para `en_linea` el 2025-11-28.

## Evidencia de GitHub Actions

1. Suba el repositorio a GitHub y abra **Actions**.
2. El flujo automático en `push`/`pull_request` valida `ventas.csv` corregido y debe quedar verde.
3. Para demostrar el bloqueo con el anexo, seleccione **Run workflow** y elija `ventas_anexo.csv`; la ejecución debe quedar roja en el paso **Validar archivo de ventas**.
4. Guarde capturas de ambas ejecuciones. El flujo manual usa el mismo código y las mismas reglas, solo cambia el archivo seleccionado.

## Reglas implementadas

1. Columnas exactas y en el orden definido: `id_venta, fecha, canal, monto`.
2. `id_venta` sin nulos ni duplicados.
3. `canal` únicamente `tienda` o `en_linea`.
4. Montos numéricos, no negativos y ninguna venta superior a COP 5.000.000.
5. Total diario por canal no superior a 3 veces el promedio de los días anteriores disponibles. El primer día de cada canal es la línea base y no se evalúa por falta de historia.

## Supuesto de negocio importante

El contrato define `monto` en pesos colombianos (COP), no en centavos. El cambio del 27 de noviembre que envió centavos enteros debe normalizarse en el sistema productor antes de publicar el dato. Para la demostración, los tres montos de `en_linea` del 28 de noviembre se dividieron por 100. No se modifica `tienda`.

## Limitación conocida

La regla de anomalía compara cada fecha con el promedio simple de los totales diarios previos observados por canal. En producción convendría acordar una ventana histórica mínima, tratamiento de días sin ventas, calendario comercial y umbrales por temporada con el área de negocio.
