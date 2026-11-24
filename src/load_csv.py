"""Carga inicial ÚNICA del CSV a MySQL (el único uso permitido del CSV)."""
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from db import engine

ROOT = Path(__file__).parent.parent
COLS = {"date": "fecha_hora", "Usage_kWh": "consumo_kwh",
        "Lagging_Current_Reactive.Power_kVarh": "reactiva_inductiva",
        "Leading_Current_Reactive_Power_kVarh": "reactiva_capacitiva",
        "CO2(tCO2)": "co2", "Lagging_Current_Power_Factor": "fp_inductivo",
        "Leading_Current_Power_Factor": "fp_capacitivo", "NSM": "nsm"}


def run_schema(eng):
    with eng.begin() as c:
        for stmt in (ROOT / "sql/schema.sql").read_text().split(";"):
            if stmt.strip():
                c.execute(text(stmt))


def catalog(eng, table, df, cols):
    """Inserta valores únicos en una tabla catálogo y devuelve {nombre: id}."""
    df[cols].drop_duplicates().to_sql(table, eng, if_exists="append", index=False)
    return pd.read_sql(f"SELECT id, nombre FROM {table}", eng).set_index("nombre").id


def main(csv=ROOT / "data/steel.csv"):
    raw = pd.read_csv(csv)
    raw["date"] = pd.to_datetime(raw["date"], format="%d/%m/%Y %H:%M")
    raw["es_fin_de_semana"] = raw.WeekStatus.eq("Weekend")
    run_schema(engine(""))
    eng = engine()
    tipos = catalog(eng, "tipo_carga", raw.rename(columns={"Load_Type": "nombre"}), ["nombre"])
    dias = catalog(eng, "dia_semana", raw.rename(columns={"Day_of_week": "nombre"}),
                   ["nombre", "es_fin_de_semana"])
    df = raw.rename(columns=COLS)[list(COLS.values())]
    df["id_tipo_carga"] = raw.Load_Type.map(tipos)
    df["id_dia"] = raw.Day_of_week.map(dias)
    df.to_sql("mediciones", eng, if_exists="append", index=False, chunksize=5000)
    print(pd.read_sql("SELECT COUNT(*) AS filas FROM mediciones", eng))


if __name__ == "__main__":
    main(*sys.argv[1:])
