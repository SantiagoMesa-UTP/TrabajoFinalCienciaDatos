"""Análisis completo: consultas SQL -> calidad -> EDA -> modelado -> conclusiones.

Pregunta: ¿qué tan bien se predice el consumo (kWh) de una planta siderúrgica?
Ejecutar desde la raíz:  py src/analisis.py   (MySQL debe estar corriendo)
Todos los datos se leen desde MySQL; el CSV solo se usa en load_csv.py.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import model
import queries
from db import query

FIG = Path(__file__).parent.parent / "figures"
sns.set_theme()


def titulo(txt):
    print(f"\n{'=' * 60}\n{txt}\n{'=' * 60}")


def guardar(nombre):
    """Guarda la figura actual para las diapositivas y la cierra."""
    plt.tight_layout()
    plt.savefig(FIG / f"{nombre}.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------- 1. SQL
# Consultas con JOIN / GROUP BY (definidas en queries.py) para la sustentación.
titulo("1. CONSULTAS SQL")
for nombre in ["CALIDAD", "POR_TIPO_CARGA", "POR_DIA"]:
    print(f"\n-- {nombre}\n", query(getattr(queries, nombre)).to_string(index=False))

# ---------------------------------------------------------------- 2. Calidad
# Dataset completo (3 tablas unidas con JOIN) para el análisis en pandas.
df = model.load()
titulo("2. CALIDAD Y ESTADÍSTICA DESCRIPTIVA")
print("Nulos:", df.isna().sum().sum(), "| Duplicados:", df.duplicated().sum())
print(df.describe().T.round(2).to_string())

# ---------------------------------------------------------------- 3. EDA
# Distribución, patrón horario y relación con el tipo de carga.
fig, ax = plt.subplots(1, 3, figsize=(16, 4))
sns.histplot(df.consumo_kwh, bins=50, ax=ax[0]).set_title("Distribución del consumo (kWh)")
horas = query(queries.POR_HORA)  # agregación hecha en MySQL
ax[1].plot(horas.hora, horas.kwh_prom, marker="o")
ax[1].set(title="Consumo medio por hora", xlabel="hora")
sns.boxplot(data=df, x="tipo_carga", y="consumo_kwh", ax=ax[2]).set_title("Consumo por tipo de carga")
guardar("eda_distribuciones")

# Correlaciones: el CO2 casi coincide con el kWh, por eso se excluye del modelo.
plt.figure(figsize=(8, 6))
sns.heatmap(df[model.NUM[:-1] + ["co2", "consumo_kwh"]].corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0)
guardar("eda_correlaciones")

# ---------------------------------------------------------------- 4. Modelo
# Partición temporal 80/20: entrena con el pasado, evalúa con el futuro.
titulo("4. MODELADO")
res, ajustados, test = model.evaluate(df)
print(res)

# Real vs. predicho del mejor modelo.
pred = ajustados["Random Forest"].predict(test[model.NUM + model.CAT])
plt.figure(figsize=(5, 5))
plt.scatter(test.consumo_kwh, pred, s=3, alpha=0.4)
plt.plot([0, 120], [0, 120], "r")
plt.xlabel("kWh real"); plt.ylabel("kWh predicho"); plt.title("Random Forest")
guardar("modelo_real_vs_predicho")

# Importancia de variables: qué explica el consumo.
rf = ajustados["Random Forest"]
imp = pd.Series(rf[-1].feature_importances_, rf[0].get_feature_names_out()).sort_values()
imp.plot.barh(title="Importancia de variables")
guardar("modelo_importancias")
print("\nImportancias:\n", imp.round(3).sort_values(ascending=False).to_string())

# ---------------------------------------------------------------- 5. Sensibilidad
# Load_Type se asigna según el consumo; se repite el modelo sin esa variable.
titulo("5. SENSIBILIDAD: SIN tipo_carga")
print(model.evaluate(df, cat=[])[0])
