import pandas as pd
import pytest

from validar_ventas import (
    validar,
    regla_columnas,
    regla_id_venta,
    regla_canales,
    regla_monto_individual,
    regla_total_diario,
)


@pytest.fixture
def ventas_validas():
    return pd.DataFrame([
        {"id_venta": 1, "fecha": "2025-11-25", "canal": "tienda", "monto": 120000},
        {"id_venta": 2, "fecha": "2025-11-25", "canal": "en_linea", "monto": 180000},
        {"id_venta": 3, "fecha": "2025-11-26", "canal": "tienda", "monto": 130000},
        {"id_venta": 4, "fecha": "2025-11-26", "canal": "en_linea", "monto": 190000},
        {"id_venta": 5, "fecha": "2025-11-27", "canal": "tienda", "monto": 125000},
        {"id_venta": 6, "fecha": "2025-11-27", "canal": "en_linea", "monto": 200000},
    ])


def test_archivo_valido_pasa(ventas_validas):
    assert validar(ventas_validas) == []


def test_columnas_incorrectas_falla(ventas_validas):
    ventas_validas.rename(columns={"monto": "valor"}, inplace=True)
    assert regla_columnas(ventas_validas)


def test_id_nulo_falla(ventas_validas):
    ventas_validas.loc[0, "id_venta"] = None
    assert any("nulos" in e for e in regla_id_venta(ventas_validas))


def test_id_duplicado_falla(ventas_validas):
    ventas_validas.loc[1, "id_venta"] = 1
    assert any("duplicados" in e for e in regla_id_venta(ventas_validas))


def test_canal_invalido_falla(ventas_validas):
    ventas_validas.loc[0, "canal"] = "web"
    assert regla_canales(ventas_validas)


def test_monto_mayor_a_limite_falla(ventas_validas):
    ventas_validas.loc[0, "monto"] = 5_000_001
    assert any("superiores" in e for e in regla_monto_individual(ventas_validas))


def test_total_diario_anomalo_falla(ventas_validas):
    ventas_validas.loc[len(ventas_validas)] = [7, "2025-11-28", "en_linea", 2_000_000]
    assert any("anómalo" in e for e in regla_total_diario(ventas_validas))


def test_csv_anexo_falla_por_montos_y_total():
    df = pd.read_csv("ventas_anexo.csv")
    errores = validar(df)
    assert any("superiores" in e for e in errores)
    assert any("anómalo" in e for e in errores)
