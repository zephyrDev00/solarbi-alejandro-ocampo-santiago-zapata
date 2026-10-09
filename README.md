# SolarBI Pascual - consulta Inteligencia de Negocios

**Integrantes:** Alejandro Ocampo Narváez y Santiago Zapata Zapata  
**Curso:** Inteligencia de Negocios · Grupo 01 · 2026-II

Práctica reproducible con telemetría simulada de inversor de 5 kWp. El mismo conjunto limpio alimenta una vista operativa de Grafana y una vista de negocio en Power BI. Las contraseñas se mantienen fuera del repositorio.

## Requisitos y ejecución

1. Instalar Python 3.10+, PostgreSQL 14+ y `pip install -r requirements.txt`.
2. Crear una base `solarbi` y configurar la variable local `SOLARBI_DSN` (ver `.env.example`; no subir credenciales).
3. Desde esta carpeta ejecutar `python etl/run_etl.py`. Si falta Bronze, el proceso la crea con semilla determinista; nunca sobrescribe el CSV crudo. El ETL valida, exporta `data/silver/lectura_5min.csv`, carga Silver y Gold usando UPSERT.
4. Ejecutar el mismo comando de nuevo. Las claves primarias compuestas conservan los conteos. Comprobar con `SELECT count(*) FROM silver.lectura_5min;` y `SELECT count(*) FROM dwh.fact_energia_dia;`.
5. En Power BI, conectarse a PostgreSQL, usar las medidas DAX de `powerbi/medidas.dax` y construir tarjeta de energía, línea diaria y tarjeta de calidad.
6. En Grafana OSS, crear un data source PostgreSQL de solo lectura, importar `grafana/dashboard.json` y seleccionar el rango 5-7 octubre 2026.

## Datos

Bronze contiene tres días a intervalos de 5 min, con potencia negativa, valor faltante y filas duplicadas inyectadas. Sus horas sin zona se interpretan como America/Bogota y se guardan en PostgreSQL `timestamptz`. Reglas Silver: fecha/dispositivo interpretables; clave natural no repetida; no faltantes/no numéricos; límites físicos P 0-5.5 kW, irradiancia 0-1200 W/m² y temperatura -20-100 °C. Se registra un motivo excluyente por fila. La energía es `sum(p_ac_kw * 5 / 60)`.

## Reparto sugerido para revisión de la pareja

| Integrante | Aporte asignado para confirmar |
|---|---|
| Alejandro Ocampo Narváez | Revisión de consulta y fuentes; validar gobernanza y métricas. |
| Santiago Zapata Zapata | Revisión de ETL, SQL y configuración de tableros. |

El reparto y el historial de commits deben reflejar lo que efectivamente haga cada integrante. Publiquen este directorio en el repositorio público `solarbi-alejandro-ocampo-santiago-zapata`, añadan al otro integrante como colaborador y generen al menos tres commits descriptivos por persona. No se ha creado ni publicado ese repositorio desde este paquete.

## Seguridad y límites de la demostración

Los datos son simulados y no contienen datos personales. El JSON apunta a un data source con UID `solarbi-postgres`, que se crea o ajusta al importar. Deben probarse alertas, permisos y conectividad en las instalaciones reales. No se incluye un `.pbix` binario ni un archivo de dashboard real de una instancia de Power BI/Grafana; se incluyen configuración, medidas y SQL reproducibles.
