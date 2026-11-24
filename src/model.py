"""Preparación de variables, entrenamiento y evaluación de los modelos."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

import queries
from db import query

NUM = ["reactiva_inductiva", "reactiva_capacitiva", "fp_inductivo", "fp_capacitivo", "hora", "es_fin_de_semana"]
CAT = ["tipo_carga"]  # CO2 se excluye: es casi proporcional al consumo (fuga de información)


def load():
    return query(queries.DATASET)


def split(df, frac=0.8):
    """Partición temporal: entrena con el pasado, prueba con el futuro."""
    k = int(len(df) * frac)
    return df.iloc[:k], df.iloc[k:]


def models(cat=CAT):
    prep = lambda: ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), cat)], remainder="passthrough")
    return {"Regresión lineal": make_pipeline(prep(), LinearRegression()),
            "Random Forest": make_pipeline(prep(), RandomForestRegressor(200, min_samples_leaf=5, n_jobs=-1, random_state=0))}


def evaluate(df, cat=CAT):
    """Entrena ambos modelos y devuelve (tabla de métricas, modelos entrenados, y_test)."""
    train, test = split(df)
    cols = NUM + cat
    fitted, rows = {}, {}
    for name, m in models(cat).items():
        m.fit(train[cols], train.consumo_kwh)
        pred = m.predict(test[cols])
        fitted[name] = m
        rows[name] = {"R2": r2_score(test.consumo_kwh, pred),
                      "RMSE": mean_squared_error(test.consumo_kwh, pred) ** 0.5,
                      "MAE": mean_absolute_error(test.consumo_kwh, pred)}
    return pd.DataFrame(rows).T.round(3), fitted, test
