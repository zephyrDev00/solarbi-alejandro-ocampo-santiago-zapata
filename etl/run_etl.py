"""ETL idempotente SolarBI: Bronze CSV -> validación -> PostgreSQL Silver/Gold."""
import csv
import os
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze" / "telemetria.csv"
SILVER_CSV = ROOT / "data" / "silver" / "lectura_5min.csv"

def preparar():
    seen, valid, rejects = set(), [], Counter()
    rejects_day = defaultdict(int)
    with BRONZE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        # Llave natural: timestamp + dispositivo. La primera copia prevalece.
        try:
            ts = datetime.fromisoformat(row["ts"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=ZoneInfo("America/Bogota"))
            device = int(row["dispositivo_id"])
        except Exception:
            rejects["formato"] += 1; continue
        key = (ts, device)
        if key in seen:
            rejects["duplicado"] += 1; rejects_day[ts.date()] += 1; continue
        seen.add(key)
        try:
            p, irr, temp = (Decimal(row[c]) for c in ("p_ac_kw", "irradiancia_wm2", "temp_modulo_c"))
        except Exception:
            rejects["faltante_o_no_numerico"] += 1; rejects_day[ts.date()] += 1; continue
        if not (Decimal("0") <= p <= Decimal("5.5") and Decimal("0") <= irr <= Decimal("1200") and Decimal("-20") <= temp <= Decimal("100")):
            rejects["rango_fisico"] += 1; rejects_day[ts.date()] += 1; continue
        valid.append((ts, device, p, irr, temp))
    with SILVER_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["ts", "dispositivo_id", "p_ac_kw", "irradiancia_wm2", "temp_modulo_c"])
        for r in valid: w.writerow(r)
    return rows, valid, rejects, rejects_day

def cargar(valid, rejects, rejects_day, total):
    try:
        import psycopg
    except ImportError:
        print("Falta psycopg. Instale: pip install 'psycopg[binary]'"); sys.exit(2)
    dsn = os.getenv("SOLARBI_DSN")
    if not dsn:
        print("Configure SOLARBI_DSN con una cadena PostgreSQL local (no la suba a Git)."); sys.exit(2)
    byday = defaultdict(list)
    for r in valid: byday[r[0].date()].append(r)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
            cur.executemany("""INSERT INTO silver.lectura_5min(ts, dispositivo_id, p_ac_kw, irradiancia_wm2, temp_modulo_c)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT (ts, dispositivo_id) DO UPDATE SET
                p_ac_kw=EXCLUDED.p_ac_kw, irradiancia_wm2=EXCLUDED.irradiancia_wm2, temp_modulo_c=EXCLUDED.temp_modulo_c""", valid)
            for day, rows in byday.items():
                # Energía válida: suma kW * (5/60) h. Validez contra 288 muestras esperadas.
                energy = sum((r[2] * Decimal(5) / Decimal(60) for r in rows), Decimal(0))
                rejected_day = rejects_day[day]
                pct = (Decimal(len(rows)) / Decimal(len(rows) + rejected_day) * 100).quantize(Decimal("0.01"))
                cur.execute("""INSERT INTO dwh.fact_energia_dia(fecha, dispositivo_id, energia_kwh, pct_datos_validos, lecturas_validas, lecturas_rechazadas)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (fecha, dispositivo_id) DO UPDATE SET
                    energia_kwh=EXCLUDED.energia_kwh, pct_datos_validos=EXCLUDED.pct_datos_validos,
                    lecturas_validas=EXCLUDED.lecturas_validas, lecturas_rechazadas=EXCLUDED.lecturas_rechazadas""",
                    (day, rows[0][1], energy, pct, len(rows), rejected_day))
            cur.execute("SELECT count(*) FROM silver.lectura_5min"); silver_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM dwh.fact_energia_dia"); gold_count = cur.fetchone()[0]
    print(f"Leídas: {total}; válidas: {len(valid)}; rechazadas (motivo excluyente): {dict(rejects)}")
    print(f"% válidas: {len(valid)/total*100:.2f}% | silver rows: {silver_count} | gold rows: {gold_count}")

def main():
    if not BRONZE.exists():
        from simulador import main as generar
        generar()
    rows, valid, rejects, rejects_day = preparar()
    cargar(valid, rejects, rejects_day, len(rows))

if __name__ == "__main__": main()
