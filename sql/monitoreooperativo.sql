CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS dwh;
CREATE TABLE IF NOT EXISTS silver.lectura_5min (
  ts timestamptz NOT NULL,
  dispositivo_id integer NOT NULL,
  p_ac_kw numeric(8,3) NOT NULL CHECK (p_ac_kw BETWEEN 0 AND 5.5),
  irradiancia_wm2 numeric(8,1) NOT NULL CHECK (irradiancia_wm2 BETWEEN 0 AND 1200),
  temp_modulo_c numeric(6,1) NOT NULL CHECK (temp_modulo_c BETWEEN -20 AND 100),
  PRIMARY KEY (ts, dispositivo_id)
);
CREATE INDEX IF NOT EXISTS ix_lectura_5min_device_ts ON silver.lectura_5min(dispositivo_id, ts);
CREATE TABLE IF NOT EXISTS dwh.fact_energia_dia (
  fecha date NOT NULL,
  dispositivo_id integer NOT NULL,
  energia_kwh numeric(12,4) NOT NULL,
  pct_datos_validos numeric(5,2) NOT NULL CHECK (pct_datos_validos BETWEEN 0 AND 100),
  lecturas_validas integer NOT NULL,
  lecturas_rechazadas integer NOT NULL,
  PRIMARY KEY (fecha, dispositivo_id)
);