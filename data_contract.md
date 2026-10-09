# Contrato de datos SolarBI - telemetría de inversor

**Propósito:** monitoreo operativo y agregación diaria para análisis de energía.  
**Propietario provisional:** product owner del proyecto de aula (asignación por validar).  
**Custodio técnico:** data engineer del equipo (asignación por validar).  
**Frecuencia:** una lectura cada 5 minutos por dispositivo.  
**Zona horaria de entrada:** hora local `America/Bogota`; Silver almacena `timestamptz`.

| Campo | Tipo | Unidad / regla |
|---|---|---|
| `ts` | timestamp | Marca temporal; clave junto con dispositivo; no nula |
| `dispositivo_id` | integer | Identificador estable; positivo y no nulo |
| `p_ac_kw` | decimal | Potencia AC kW; 0 a 5.5 para dispositivo de 5 kWp |
| `irradiancia_wm2` | decimal | W/m²; 0 a 1200 |
| `temp_modulo_c` | decimal | °C; -20 a 100 |

## Claves y calidad

Clave natural Silver: (`ts`, `dispositivo_id`). La telemetría duplicada se rechaza por clave; no se sobrescribe Bronze. Faltantes y no numéricos se rechazan; rango físico se valida; cada registro rechazado recibe una sola causa prioritaria para que conteos sumen el total. El porcentaje válido es válidas / leídas * 100. Gold agrupa por (`fecha`, `dispositivo_id`), calcula `energia_kwh = sum(p_ac_kw * 5/60)` y conserva conteos de válidas y rechazadas.

## Cambio y privacidad

Todo cambio de columna, unidad, frecuencia o clave requiere versión nueva, comunicación previa, validación en Silver y ajuste de modelo/tableros. No incluir identificadores personales en la telemetría. El conjunto actual es sintético y no contiene personal real.
