"""Consultas SQL del proyecto, nombradas para mostrarlas en la sustentación."""

DATASET = """
SELECT m.fecha_hora, m.consumo_kwh, m.reactiva_inductiva, m.reactiva_capacitiva,
       m.co2, m.fp_inductivo, m.fp_capacitivo, m.nsm / 3600 AS hora,
       t.nombre AS tipo_carga, d.nombre AS dia, d.es_fin_de_semana
FROM mediciones m
JOIN tipo_carga t ON t.id = m.id_tipo_carga
JOIN dia_semana d ON d.id = m.id_dia
ORDER BY m.fecha_hora
"""

POR_TIPO_CARGA = """
SELECT t.nombre AS tipo_carga, COUNT(*) AS n, ROUND(AVG(m.consumo_kwh), 2) AS kwh_prom,
       ROUND(AVG(m.fp_inductivo), 1) AS fp_prom
FROM mediciones m JOIN tipo_carga t ON t.id = m.id_tipo_carga
GROUP BY t.nombre ORDER BY kwh_prom
"""

POR_HORA = """
SELECT FLOOR(nsm / 3600) AS hora, ROUND(AVG(consumo_kwh), 2) AS kwh_prom
FROM mediciones GROUP BY hora ORDER BY hora
"""

POR_DIA = """
SELECT d.nombre AS dia, d.es_fin_de_semana, ROUND(AVG(m.consumo_kwh), 2) AS kwh_prom
FROM mediciones m JOIN dia_semana d ON d.id = m.id_dia
GROUP BY d.id ORDER BY d.es_fin_de_semana, kwh_prom
"""

CALIDAD = """
SELECT COUNT(*) AS filas, COUNT(DISTINCT fecha_hora) AS fechas_unicas,
       MIN(fecha_hora) AS desde, MAX(fecha_hora) AS hasta,
       SUM(consumo_kwh <= 0) AS consumo_no_positivo, SUM(fp_inductivo < 0 OR fp_inductivo > 100) AS fp_fuera_rango
FROM mediciones
"""
