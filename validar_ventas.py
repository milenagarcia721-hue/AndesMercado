"""Validaciones de calidad para el archivo de ventas de AndesMercado."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

import pandas as pd

COLUMNAS_ESPERADAS = ["id_venta", "fecha", "canal", "monto"]
CANALES_VALIDOS = {"tienda", "en_linea"}
MONTO_MAXIMO_COP = 5_000_000.0
FACTOR_ANOMALIA_DIARIA = 3.0


def regla_columnas(df: pd.DataFrame) -> list[str]:
    if list(df.columns) != COLUMNAS_ESPERADAS:
        return [f"Columnas inválidas. Esperadas exactamente: {COLUMNAS_ESPERADAS}; recibidas: {list(df.columns)}"]
    return []


def regla_id_venta(df: pd.DataFrame) -> list[str]:
    errores = []
    if "id_venta" not in df.columns:
        return ["No se puede validar id_venta porque la columna no existe."]
    if df["id_venta"].isna().any():
        errores.append("id_venta contiene valores nulos.")
    if df["id_venta"].duplicated().any():
        errores.append("id_venta contiene valores duplicados.")
    return errores


def regla_canales(df: pd.DataFrame) -> list[str]:
    if "canal" not in df.columns:
        return ["No se puede validar canal porque la columna no existe."]
    encontrados = set(df["canal"].dropna().astype(str).unique())
    invalidos = encontrados - CANALES_VALIDOS
    errores = []
    if df["canal"].isna().any():
        errores.append("canal contiene valores nulos.")
    if invalidos:
        errores.append(f"canal contiene valores no permitidos: {sorted(invalidos)}.")
    return errores


def regla_monto_individual(df: pd.DataFrame) -> list[str]:
    if "monto" not in df.columns:
        return ["No se puede validar monto porque la columna no existe."]
    montos = pd.to_numeric(df["monto"], errors="coerce")
    errores = []
    if montos.isna().any():
        errores.append("monto contiene valores nulos o no numéricos.")
    if (montos.dropna() < 0).any():
        errores.append("monto contiene valores negativos.")
    altos = montos[montos > MONTO_MAXIMO_COP]
    if not altos.empty:
        errores.append(
            f"Hay {len(altos)} ventas individuales superiores a COP {MONTO_MAXIMO_COP:,.0f}."
        )
    return errores


def regla_total_diario(df: pd.DataFrame) -> list[str]:
    """Compara cada día/canal con 3x el promedio de días anteriores disponibles.
    El primer día de cada canal se toma como línea base y no se evalúa por falta de historia.
    """
    requeridas = {"fecha", "canal", "monto"}
    if not requeridas.issubset(df.columns):
        return ["No se puede validar total diario: faltan fecha, canal o monto."]
    datos = df.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce")
    datos["monto"] = pd.to_numeric(datos["monto"], errors="coerce")
    if datos["fecha"].isna().any() or datos["monto"].isna().any():
        return ["No se puede validar total diario por fechas o montos inválidos."]
    totales = (
        datos.groupby([datos["fecha"].dt.date, "canal"])["monto"]
        .sum()
        .reset_index(name="total")
        .sort_values("fecha")
    )
    errores = []
    for canal, grupo in totales.groupby("canal"):
        historicos = []
        for fila in grupo.itertuples(index=False):
            if historicos:
                promedio = sum(historicos) / len(historicos)
                limite = FACTOR_ANOMALIA_DIARIA * promedio
                if fila.total > limite:
                    errores.append(
                        f"Total diario anómalo para canal '{canal}' el {fila.fecha}: "
                        f"COP {fila.total:,.2f} > 3x promedio previo COP {promedio:,.2f} "
                        f"(límite COP {limite:,.2f})."
                    )
            historicos.append(float(fila.total))
    return errores


REGLAS: list[tuple[str, Callable[[pd.DataFrame], list[str]]]] = [
    ("columnas", regla_columnas),
    ("id_venta", regla_id_venta),
    ("canal", regla_canales),
    ("monto_individual", regla_monto_individual),
    ("total_diario", regla_total_diario),
]


def validar(df: pd.DataFrame) -> list[str]:
    """Devuelve una lista de reglas incumplidas con su detalle."""
    errores = []
    # Si las columnas no coinciden, se reporta y se evita que otras reglas fallen por KeyError.
    errores.extend(regla_columnas(df))
    if list(df.columns) != COLUMNAS_ESPERADAS:
        return errores
    for _, regla in REGLAS[1:]:
        errores.extend(regla(df))
    return errores


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida calidad de datos de ventas AndesMercado.")
    parser.add_argument("archivo", nargs="?", default="ventas.csv", help="Ruta del CSV que se validará.")
    args = parser.parse_args()
    ruta = Path(args.archivo)
    if not ruta.exists():
        print(f"ERROR: no existe el archivo: {ruta}", file=sys.stderr)
        return 1
    try:
        df = pd.read_csv(ruta)
    except Exception as exc:
        print(f"ERROR: no fue posible leer el CSV: {exc}", file=sys.stderr)
        return 1

    errores = validar(df)
    if errores:
        print(f"VALIDACIÓN FALLIDA: {len(errores)} incumplimiento(s) en {ruta}")
        for error in errores:
            print(f"- {error}")
        return 1

    print(f"VALIDACIÓN EXITOSA: {ruta} cumple todas las reglas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
