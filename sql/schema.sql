DROP DATABASE IF EXISTS acero;
CREATE DATABASE acero CHARACTER SET utf8mb4;
USE acero;

CREATE TABLE tipo_carga (
  id TINYINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE dia_semana (
  id TINYINT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(10) NOT NULL UNIQUE,
  es_fin_de_semana BOOLEAN NOT NULL
);

CREATE TABLE mediciones (
  id INT PRIMARY KEY AUTO_INCREMENT,
  fecha_hora DATETIME NOT NULL,
  consumo_kwh DECIMAL(8,2) NOT NULL,
  reactiva_inductiva DECIMAL(8,2) NOT NULL,
  reactiva_capacitiva DECIMAL(8,2) NOT NULL,
  co2 DECIMAL(6,2) NOT NULL,
  fp_inductivo DECIMAL(6,2) NOT NULL,
  fp_capacitivo DECIMAL(6,2) NOT NULL,
  nsm INT NOT NULL COMMENT 'segundos desde medianoche',
  id_tipo_carga TINYINT NOT NULL,
  id_dia TINYINT NOT NULL,
  FOREIGN KEY (id_tipo_carga) REFERENCES tipo_carga(id),
  FOREIGN KEY (id_dia) REFERENCES dia_semana(id),
  INDEX (fecha_hora)
);
