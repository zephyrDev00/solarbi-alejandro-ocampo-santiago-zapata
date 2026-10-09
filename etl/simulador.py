"""Genera tres días de telemetría simulada. Nunca sobrescribe Bronze."""
import csv
import math
import os
import random
from datetime import datetime, timedelta

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "bronze", "telemetria.csv")

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT):
        print(f"Bronze existente, se conserva sin cambios: {OUT}")
        return
    random.seed(20261005)
    inicio = datetime(2026, 10, 5)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts", "dispositivo_id", "p_ac_kw", "irradiancia_wm2", "temp_modulo_c"])
        for i in range(3 * 288):
            ts = inicio + timedelta(minutes=5 * i)
            sol = max(0.0, math.sin(math.pi * (ts.hour + ts.minute / 60 - 6) / 12))
            irr = round(1000 * sol * random.uniform(.7, 1), 1)
            p_ac = round(5 * irr / 1000 * random.uniform(.80, .90), 3)
            fila = [ts.isoformat(sep=" "), 1, p_ac, irr, round(22 + 30 * sol, 1)]
            r = random.random()
            if r < .02:
                fila[2] = -1
            elif r < .04:
                fila[3] = ""
            w.writerow(fila)
            if r > .98:
                w.writerow(fila)
    print(f"Bronze creado: {OUT}")

if __name__ == "__main__":
    main()
