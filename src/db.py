"""Conexión a MySQL y helper de consultas (único punto de acceso a los datos)."""
import os
import pandas as pd
from sqlalchemy import create_engine

URL = os.getenv("MYSQL_URL", "mysql+pymysql://root:@localhost:3306/")


def engine(db="acero"):
    return create_engine(URL + db)


def query(sql, **params):
    """Ejecuta SQL y devuelve un DataFrame."""
    with engine().connect() as c:
        return pd.read_sql(sql, c, params=params or None)
