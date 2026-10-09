from pathlib import Path
import csv, statistics
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image, KeepTogether)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image as PILImage, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'; DOCS.mkdir(exist_ok=True)
PDF = DOCS / 'Alejandro_Ocampo_Narvaez_Santiago_Zapata_Zapata_Consulta_BI_G01.pdf'

sources = [
('Grafana Labs. PostgreSQL data source: query editor and macros.', 'https://grafana.com/docs/grafana/latest/datasources/postgres/query-editor/'),
('Grafana Labs. Alerting notifications and contact points.', 'https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/'),
('Microsoft Learn. Power BI data alerts.', 'https://learn.microsoft.com/en-us/power-bi/consumer/end-user-alerts'),
('Microsoft Learn. Power BI Desktop projects (PBIP).', 'https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview'),
('Microsoft Learn. Query folding guidance in Power Query.', 'https://learn.microsoft.com/en-us/power-bi/guidance/power-query-folding'),
('DAMA International. DAMA-DMBOK and data management.', 'https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/'),
('Congreso de Colombia. Ley Estatutaria 1581 de 2012.', 'https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981'),
('OASIS. MQTT Version 5.0, OASIS Standard.', 'https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html'),
('Git project. Pro Git Book, branching and merging.', 'https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell'),
('PostgreSQL Global Development Group. INSERT / ON CONFLICT.', 'https://www.postgresql.org/docs/current/sql-insert.html'),
('Apache Software Foundation. Airflow documentation.', 'https://airflow.apache.org/docs/apache-airflow/stable/'),
('Grafana Labs. PostgreSQL data source configuration and least privilege.', 'https://grafana.com/docs/grafana/latest/datasources/postgres/configure/'),
]

answers = [
('D1. ¿Qué es Grafana?', 'Grafana es una plataforma para consultar, visualizar y alertar sobre datos de fuentes distintas. Un <i>data source</i> conecta PostgreSQL u otros sistemas; un <i>panel</i> presenta una consulta; un <i>dashboard</i> organiza paneles; las variables parametrizan filtros como sitio o dispositivo; y Alerting evalúa reglas y enruta avisos a <i>contact points</i>. Grafana OSS se instala y administra por cuenta propia, con el núcleo abierto; Grafana Cloud es un servicio hospedado con operación gestionada y planes/servicios comerciales. Para SolarBI, OSS sirve para la práctica y Cloud podría reducir carga operativa, sujeto a costos y conectividad. [1,2]'),
('D2. Power BI vs. Grafana', [('Criterio','Power BI','Grafana'),('Propósito','Análisis y reporting de negocio','Observabilidad y monitoreo temporal'),('Usuario','Analista, directivo, áreas de negocio','Operador, SRE, equipo técnico'),('Conexión','Conectores, Import o DirectQuery','Data sources consultados por panel'),('Modelo/lenguaje','Modelo semántico, relaciones y DAX','Consulta nativa del origen: SQL, PromQL, etc.'),('Actualización','Refresh programado/DirectQuery según fuente','Refresh de panel y consultas cercanas al tiempo real'),('Alertas','Servicio: tiles de tarjeta/KPI/medidor tras refresh','Reglas evaluadas y contact points'),('Costo','Desktop de autoría sin costo; compartir/servicio depende licencia/capacidad','OSS autogestionado; Cloud y capacidades avanzadas según plan'),('Acceso','Workspaces, permisos y RLS del modelo','Usuarios/organizaciones, roles, carpetas y permisos'),('Mejor encaje SolarBI','Yield, energía, ahorro y dirección','Potencia instantánea, disponibilidad y fallas')]),
('D3. Dashboard operativo, analítico y estratégico', 'El operativo muestra eventos recientes para actuar; el analítico explora causas e historia; el estratégico resume objetivos. Energía diaria, yield (kWh/kWp) y PR (energía real frente a energía esperada según irradiación) son analíticos; ahorro frente a una línea base es estratégico; disponibilidad (tiempo disponible / tiempo planificado) y alarmas son operativos; porcentaje válido es analítico y de calidad. El operador vería potencia y alarmas en Grafana. Dirección vería energía, yield, PR y ahorro en Power BI; calidad y disponibilidad pueden cruzar ambos según su ventana de análisis. [1,3]'),
('D4. PostgreSQL y series de tiempo', 'Grafana espera que la consulta devuelva una columna temporal llamada time y una o más series numéricas, filtradas por el rango activo y ordenadas cronológicamente. $__timeFilter(ts) se expande al intervalo seleccionado; $__timeGroup(ts,\'1h\') calcula los grupos temporales (para alias explícito se usa $__timeGroupAlias). Potencia promedio por hora: SELECT $__timeGroupAlias(ts, \'1h\'), AVG(p_ac_kw) AS "Potencia media kW" FROM silver.lectura_5min WHERE $__timeFilter(ts) AND dispositivo_id=1 GROUP BY 1 ORDER BY 1. [1]'),
('D5. Alertas', 'Grafana evalúa una regla con consulta, condición, duración y etiquetas, luego envía la notificación al contact point configurado (por ejemplo correo o webhook). Power BI Service ofrece alertas sobre tiles de tarjeta, KPI o medidor; se revisan cuando los datos se actualizan y las crea cada usuario para sí mismo. Propuesta: si el inversor reporta potencia menor de 0.001 kW durante cinco minutos entre 09:00 y 15:00 hora Colombia, notificar por correo al operador y crear una incidencia vía webhook. Confirmar irradiancia antes de escalar para reducir falsas alarmas por nubes. [2,3]'),
('G1. Gobernanza, gestión y calidad', 'Gobernanza define quién decide, responde y establece políticas sobre datos: acceso, definiciones, protección, cambios y controles. DAMA-DMBOK la ubica como función transversal relacionada con arquitectura, calidad, metadatos, seguridad e integración. Data management ejecuta las prácticas y plataformas que adquieren, mantienen y sirven datos. Data quality mide y mejora características como exactitud, completitud, validez, unicidad y oportunidad. En SolarBI, la política de unidades y responsables es gobernanza; la carga Bronze-Silver-Gold es gestión; detectar faltantes o potencia imposible es calidad. [6]'),
('G2. Roles', 'El data owner responde por el significado, uso permitido y decisiones del dominio; el steward mantiene definiciones, reglas y calidad cotidiana; el custodian opera almacenamiento, respaldo, seguridad y disponibilidad. En SolarBI, product owner puede asumir propiedad de negocio; BI analyst o data modeler puede ser steward de KPI y modelo; data engineer suele custodiar pipelines y plataforma, pero esos son encargos, no equivalencias automáticas. El equipo debe registrar responsables formales, aprobarlos con el docente/propietario del proyecto y mantener una matriz de quién define, valida y opera cada campo. [6]'),
('G3. Contrato de datos', 'El contrato debe fijar propietario y contacto; esquema y tipos; significado; unidades y zona horaria; clave; granularidad y frecuencia; rangos y nulos permitidos; reglas de calidad y umbrales; disponibilidad/retención; privacidad; versionado y aviso de cambios. Para SolarBI: ts en UTC o zona explícita, dispositivo_id estable, p_ac_kw en kW cada cinco minutos y límites acordados. Si la fuente renombra un campo sin avisar, el ETL o modelo puede fallar, cargar nulos o producir KPI erróneos sin error visible. Validación de esquema y pruebas de contrato deben bloquear Gold y advertir antes de publicar. [6]'),
('G4. RLS y acceso', 'RLS aplica filtros de filas por rol en el modelo semántico de Power BI. Ejemplo: tabla SitioUsuario con correo y sitio_key, relación al hecho, y rol con filtro DAX SitioUsuario[correo] = USERPRINCIPALNAME(); cada responsable queda limitado a sus sitios autorizados y se valida con “Ver como”. En Grafana se separan equipos y, si conviene, organizaciones; permisos por carpeta/dashboard limitan lectura o edición. Para la base, el usuario de Grafana debe tener SELECT solo sobre vistas/tablas necesarias. La seguridad de interfaz no reemplaza permisos de base ni controles de publicación. [12]'),
('G5. Ley 1581 y ética', 'Las lecturas de potencia, irradiancia y temperatura de un panel identificado como dispositivo, sin vínculo razonable a una persona, normalmente no son datos personales por sí mismas. Si se muestra qué operador atendió cada alarma, el identificador laboral asociado sí puede identificar a una persona y queda sujeto a la Ley 1581: finalidad informada, acceso limitado, calidad, seguridad, retención definida y atención de derechos. Postura del equipo: reportar desempeño técnico agregado; usar identificadores solo cuando la operación lo requiera; evitar ranking individual y exposición innecesaria; separar permisos y documentar finalidad. Confirmar con la institución su política y roles de responsable/encargado. [7]'),
('E1. ETL, ELT y capas', 'ETL transforma antes de cargar al destino; ELT carga crudo y transforma dentro del motor destino. Bronze conserva el CSV original; Silver tipa, deduplica y valida lecturas; Gold agrega energía diaria y calidad para consumo. Power Query es una herramienta de extracción y transformación y puede cargar resultados (ETL en Import); con query folding delega pasos compatibles a la base, acercándose a ELT operacionalmente. La etiqueta depende de dónde ocurre la transformación y carga, no solo del producto. [5]'),
('E2. Full, incremental e idempotencia', 'Full load reemplaza o recarga el conjunto completo y es sencillo, pero consume tiempo y recursos. Incremental procesa cambios nuevos o actualizados usando timestamp/clave de agua. Una carga es idempotente cuando repetir la misma entrada produce el mismo estado final. En fact_energia_dia, clave primaria (fecha, dispositivo_key) más INSERT ... ON CONFLICT (...) DO UPDATE evita duplicar el agregado y permite corregirlo si cambian datos del día. La misma idea aplica a lecturas con (ts, dispositivo_id). La extracción debe además usar ventana de reproceso para capturar llegadas tardías. [10]'),
('E3. Automatización ETL', [('Opción','Qué es / automatiza','Conviene cuando'),('cron / Task Scheduler','Planificador del sistema ejecuta un comando en horario fijo','Un script único, poca dependencia y servidor estable'),('Apache Airflow','Orquestador con DAG, dependencias, reintentos, logs y calendario','Varios pasos, dependencias, backfill y operación supervisada'),('Refresh programado Power BI','Servicio actualiza un modelo importado según calendario','Solo se necesita refrescar el modelo; la extracción es sencilla')]),
('E4. Query folding', 'Query folding es la traducción de transformaciones Power Query a una consulta ejecutada por el origen. PostgreSQL filtra y agrega antes de transferir menos datos, reduciendo memoria, tiempo y carga del cliente. En Power Query, clic derecho en el paso y “Ver consulta nativa” cuando esté disponible; también se inspecciona el SQL del origen o sus logs. La opción puede desaparecer tras un paso no plegable; eso no demuestra por sí solo error, pero avisa que transformaciones posteriores se ejecutan en el motor mashup. [5]'),
('I1. Arquitectura por capas', 'Flujo: inversor/sensor (dispositivo, lectura) -> gateway edge (buffer y validación básica) -> red/broker MQTT (entrega) -> almacenamiento Bronze (original) -> Silver (lecturas válidas tipadas) -> Gold (agregación diaria en PostgreSQL) -> Grafana/Power BI (consulta y visual). La lectura original se conserva en Bronze; Silver almacena observaciones válidas a 5 min; Gold contiene hechos diarios. En la práctica guiada, el simulador sustituye inversor y broker para ensayar la ruta, no demuestra hardware conectado.'),
('I2. MQTT', 'MQTT publica mensajes por tema: el productor publica y el broker los enruta a clientes suscritos, desacoplando equipos. Un topic organiza jerárquicamente el tipo de dato: pascualbravo/solar/bloqueA/inv01/p_ac_kw y .../irradiancia_wm2. QoS 0 entrega como máximo una vez (puede perderse); QoS 1 al menos una vez (puede duplicar); QoS 2 exactamente una vez en el protocolo, con más intercambio. Para telemetría periódica suele bastar QoS 1 si el consumidor deduplica por timestamp/dispositivo; alarmas críticas deben diseñarse y probarse con entrega, persistencia y confirmación. [8]'),
('I3. Pila abierta IoT', 'Mosquitto es el broker MQTT; Telegraf suscribe y transforma/encamina métricas; InfluxDB o TimescaleDB almacena series temporales; Grafana consulta, grafica y alerta. PostgreSQL puede guardar dimensiones, contratos, historial relacional y hechos Gold; TimescaleDB añade capacidades de series temporales sobre PostgreSQL. En el trabajo, una sola PostgreSQL simplifica el laboratorio y Grafana la consulta directamente. Separar almacenamiento temporal y DWH solo conviene si volumen, retención o latencia justifican operar dos destinos.'),
('I4. Batch vs streaming', 'Batch agrupa ventanas y prioriza eficiencia, reconciliación y agregados; streaming procesa cada evento con baja latencia y más complejidad de estado, reintentos y duplicados. Con telemetría cada cinco minutos, Silver permite ver caídas y tendencias intradía. Gold diario suma potencia_kW × 5/60 horas para energía; simplifica comparación, pero pierde hora exacta, picos, secuencia y eventos breves. Grafana atiende mejor la serie operativa; Power BI el resumen diario y análisis de negocio. Guardar Silver evita que la agregación destruya el detalle.'),
('V1. Git y versiones', 'Git es el sistema distribuido local de versiones; GitHub aloja repositorios Git y colaboración. Repository contiene el historial y archivos; commit es un cambio identificado; branch es una línea independiente; pull request propone revisar e integrar cambios. Un .pbix es binario: Git no muestra bien diferencias ni fusiona ediciones concurrentes. PBIP separa definiciones del informe y modelo en archivos legibles, facilitando diffs; algunos artefactos siguen sujetos a límites de compatibilidad. Grafana permite exportar dashboard como JSON y versionarlo; para provisión también se pueden mantener JSON/YAML en archivos. [4,9]'),
]

def fmt(text):
    return text.replace('&', '&amp;') if not ('<b>' in text or '<i>' in text or '<br' in text) else text

def make_charts():
    csvfile = ROOT / 'data' / 'silver' / 'lectura_5min.csv'
    with csvfile.open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    # Small, deterministic report figures based on cleaned CSV, not screenshots from either application.
    w,h=1000,300; im=PILImage.new('RGB',(w,h),'white'); d=ImageDraw.Draw(im)
    d.text((25,12),'Vista previa de potencia AC (kW) - datos Silver',fill='#17324d')
    vals=[float(r['p_ac_kw']) for r in rows]
    left,top,right,bottom=55,45,980,260
    d.line((left,top,left,bottom),fill='#9aa8b5'); d.line((left,bottom,right,bottom),fill='#9aa8b5')
    for v in (0,1,2,3,4,5):
        y=bottom-int(v/5.5*(bottom-top)); d.line((left,y,right,y),fill='#e5ebf0'); d.text((20,y-7),str(v),fill='#506070')
    pts=[]
    for i,v in enumerate(vals): pts.append((left+i*(right-left)/max(1,len(vals)-1), bottom-v/5.5*(bottom-top)))
    for a,b in zip(pts,pts[1:]): d.line((a[0],a[1],b[0],b[1]),fill='#168aad',width=2)
    im.save(DOCS/'preview_potencia.png')
    # energy totals by date
    totals={}
    for r in rows:
        day=r['ts'][:10]; totals[day]=totals.get(day,0)+float(r['p_ac_kw'])*5/60
    im=PILImage.new('RGB',(750,300),'white'); d=ImageDraw.Draw(im); d.text((20,15),'Vista previa de energia diaria calculada (kWh)',fill='#17324d')
    maxv=max(totals.values());
    for i,(day,v) in enumerate(sorted(totals.items())):
        x=120+i*190; bh=int(v/maxv*180); d.rectangle((x,245-bh,x+100,245),fill='#2a9d8f'); d.text((x,255),day,fill='#243746'); d.text((x+5,225-bh),f'{v:.1f}',fill='#243746')
    im.save(DOCS/'preview_energia.png')

def build():
    make_charts()
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Cover',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=23,leading=29,textColor=colors.HexColor('#18324b'),alignment=TA_CENTER,spaceAfter=14))
    styles.add(ParagraphStyle(name='Sub',parent=styles['Normal'],fontSize=12,leading=17,alignment=TA_CENTER,textColor=colors.HexColor('#426174'),spaceAfter=8))
    styles.add(ParagraphStyle(name='H1x',parent=styles['Heading1'],fontSize=16,leading=20,textColor=colors.HexColor('#18324b'),spaceBefore=10,spaceAfter=8,keepWithNext=True))
    styles.add(ParagraphStyle(name='H2x',parent=styles['Heading2'],fontSize=10.5,leading=13,textColor=colors.HexColor('#177e89'),spaceBefore=5,spaceAfter=3,keepWithNext=True))
    styles.add(ParagraphStyle(name='Bodyx',parent=styles['BodyText'],fontSize=8.7,leading=12,spaceAfter=4,textColor=colors.HexColor('#263746')))
    styles.add(ParagraphStyle(name='Smallx',parent=styles['BodyText'],fontSize=7.4,leading=9.5,spaceAfter=2))
    styles.add(ParagraphStyle(name='SmallHeadx',parent=styles['BodyText'],fontSize=7.4,leading=9.5,spaceAfter=2,textColor=colors.white))
    story=[]
    story += [Spacer(1,.65*inch),Paragraph('INSTITUCIÓN UNIVERSITARIA<br/>PASCUAL BRAVO',styles['Sub']),Spacer(1,.45*inch),Paragraph('SolarBI Pascual',styles['Cover']),Paragraph('Power BI, Grafana, gobernanza, ETL e IoT',styles['Sub']),Spacer(1,.22*inch),Paragraph('Consulta resuelta y práctica reproducible',styles['H1x']),Spacer(1,.35*inch)]
    story += [Paragraph('<b>Integrantes</b>',styles['Sub']),Paragraph('Alejandro Ocampo Narváez<br/>Santiago Zapata Zapata',styles['Sub']),Spacer(1,.3*inch),Paragraph('Inteligencia de Negocios · Grupo 01 · Semestre 2026-II',styles['Sub']),Paragraph('Departamento de Sistemas Digitales · Docente: Ramiro Grisales Montoya',styles['Sub']),Paragraph('3 de octubre de 2026',styles['Sub']),Spacer(1,.6*inch),Paragraph('Caso aplicado: monitoreo operativo de potencia y detección de fallas en una planta solar simulada de 5 kWp.',styles['Bodyx']),PageBreak()]
    story += [Paragraph('Parte A · Consulta',styles['H1x']),Paragraph('Bloque 1 · Power BI y Grafana',styles['H2x'])]
    for code,content in answers:
        if code.startswith(('G1','G2','G3','G4','G5')):
            if code.startswith('G1'): story += [PageBreak(),Paragraph('Bloque 2 · Gobernanza de datos',styles['H2x'])]
        if code.startswith('E1'): story += [PageBreak(),Paragraph('Bloque 3 · Automatización de procesos ETL',styles['H2x'])]
        if code.startswith('I1'): story += [PageBreak(),Paragraph('Bloque 4 · Internet de las Cosas (IoT)',styles['H2x'])]
        if code.startswith('V1'): story += [PageBreak(),Paragraph('Bloque 5 · Control de versiones',styles['H2x'])]
        story.append(Paragraph(code,styles['H2x']))
        if isinstance(content,list):
            data=[[Paragraph(str(c),styles['SmallHeadx'] if ri==0 else styles['Smallx']) for c in row] for ri,row in enumerate(content)]
            widths=[1.1*inch,2.25*inch,2.9*inch] if len(content[0])==3 else [1.35*inch,2.45*inch,2.45*inch]
            t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#18324b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9dfe5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f7f9')])]))
            story += [t,Spacer(1,5)]
        else: story.append(Paragraph(content,styles['Bodyx']))
    story += [PageBreak(),Paragraph('Parte B · Práctica guiada',styles['H1x']),Paragraph('Datos, calidad y flujo de carga',styles['H2x'])]
    metrics=[]
    with (ROOT/'data/bronze/telemetria.csv').open(encoding='utf-8') as f: raw=list(csv.DictReader(f))
    with (ROOT/'data/silver/lectura_5min.csv').open(encoding='utf-8') as f: clean=list(csv.DictReader(f))
    seen=set(); counts={'duplicado':0,'rango_fisico':0,'faltante/no numérico':0}
    for r in raw:
        key=(r['ts'],r['dispositivo_id'])
        if key in seen: counts['duplicado']+=1; continue
        seen.add(key)
        try: p=float(r['p_ac_kw']); irr=float(r['irradiancia_wm2']); temp=float(r['temp_modulo_c'])
        except: counts['faltante/no numérico']+=1; continue
        if not (0<=p<=5.5 and 0<=irr<=1200 and -20<=temp<=100): counts['rango_fisico']+=1
    validn=len(clean); rejected=len(raw)-validn; pct=validn/len(raw)*100
    data=[['Paso / regla','Resultado verificado en CSV local'],['Bronze crudo',f'{len(raw)} filas de telemetría; periodo 5-7 oct 2026'],['Duplicados',str(counts['duplicado'])+' filas'],['Faltantes/no numéricos',str(counts['faltante/no numérico'])+' filas'],['Fuera de rango físico',str(counts['rango_fisico'])+' filas'],['Silver válidas',f'{validn} filas'],['Rechazadas total',f'{rejected} filas; reglas excluyentes'],['Datos válidos',f'{pct:.2f}% (= {validn}/{len(raw)})']]
    t=Table([[Paragraph(str(c),styles['SmallHeadx'] if ri==0 else styles['Smallx']) for c in row] for ri,row in enumerate(data)],colWidths=[2.0*inch,4.75*inch],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#18324b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9dfe5')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f7f9')]),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [t,Spacer(1,7),Paragraph('El simulador usa semilla fija y conserva Bronze si ya existe. run_etl.py aplica las mismas reglas, exporta Silver y ejecuta UPSERT por (ts, dispositivo_id) y (fecha, dispositivo_id). La expresión diaria es SELECT sum(p_ac_kw * 5.0 / 60.0). Cron solicitado: 0 0 * * * (cada día a medianoche; el servidor debe tener la zona horaria definida).',styles['Bodyx']),Paragraph('Ruta de una lectura y capa de almacenamiento',styles['H2x'])]
    flow=[['Dispositivo / inversor','Gateway / edge','Red / broker MQTT','Almacenamiento','Aplicación'],['Potencia, irradiancia, temperatura','Buffer y validación básica','Publica topic por dispositivo','Bronze: original\nSilver: lecturas válidas cada 5 min\nGold: energía y calidad por día','Grafana: operación\nPower BI: gestión']]
    flowt=Table([[Paragraph(str(c),styles['SmallHeadx'] if ri==0 else styles['Smallx']) for c in row] for ri,row in enumerate(flow)],colWidths=[1.3*inch]*5)
    flowt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#18324b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9dfe5')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story += [flowt,Paragraph('La práctica simula las primeras tres capas; no se conectó un inversor físico ni un broker MQTT.',styles['Smallx']),Paragraph('Vista generada desde el CSV Silver; no es captura de la aplicación Grafana.',styles['Smallx']),Image(str(DOCS/'preview_potencia.png'),width=6.6*inch,height=1.98*inch),Paragraph('Esta gráfica muestra las lecturas de 5 minutos tras depuración. Un cero nocturno es normal; la alarma debe limitarse a la ventana 09:00-15:00.',styles['Smallx']),Image(str(DOCS/'preview_energia.png'),width=5.7*inch,height=2.28*inch),Paragraph('La energía diaria de la vista previa se obtiene de las observaciones Silver. El panel conectado a PostgreSQL deberá mostrar la agregación Gold calculada por el ETL.',styles['Smallx'])]
    story += [PageBreak(),Paragraph('Paso 4 · Power BI',styles['H2x']),Paragraph('Construcción preparada: cargar dwh.fact_energia_dia desde PostgreSQL; usar medidas DAX en powerbi/medidas.dax para energía y porcentaje válido; representar energía diaria con línea y fecha en el eje. Las medidas y el diseño están preparados, pero el archivo PBIX/PBIP y la captura real requieren Power BI Desktop conectado a la base.',styles['Bodyx']),Paragraph('Paso 5 · Grafana',styles['H2x']),Paragraph('grafana/dashboard.json contiene la serie p_ac_kw con $__timeFilter, el panel Stat de energía y panel de ventana solar con umbral. grafana/alert_rule.yml documenta una regla de cinco minutos; importar y comprobar el UID del data source. El JSON es configuración exportable, pero todavía no ha sido abierto en una instancia Grafana y la captura de pantalla debe tomarse allí.',styles['Bodyx']),Paragraph('Paso 6 · Reflexión (máximo 10 líneas)',styles['H2x']),Paragraph('Con los mismos datos, Grafana resuelve mejor la operación: potencia en serie temporal y alerta rápida sobre anomalías. Power BI facilita los indicadores diarios, el modelo semántico y la conversación con dirección. La mayor dificultad es dejar el contrato, tipos y zona horaria consistentes; también es necesario configurar conexión y permisos. Para el operador usaríamos Grafana con umbrales y responsable de guardia; para un directivo usaríamos Power BI con energía, yield, PR, ahorro y calidad agregados.',styles['Bodyx']),Paragraph('Parte C · Repositorio en GitHub',styles['H1x']),Paragraph('Repositorio local de entrega propuesto: solarbi-alejandro-ocampo-santiago-zapata. El paquete incluye README, .gitignore, simulador, ETL, SQL, datos y configuración de Grafana/Power BI. Enlace GitHub pendiente de publicación por la pareja. Para completar los requisitos, publicar el directorio, añadir el compañero como colaborador, aceptar invitación, realizar mínimo tres commits por persona y pegar capturas reales de Collaborators y del historial con ambos autores. No se afirma que la cuenta o esas capturas existan.',styles['Bodyx']),Paragraph('<b>Evidencias a completar antes de Classroom</b>: (1) captura Power BI con ambas tarjetas y línea, (2) captura Grafana con potencia y Stat, (3) colaboradores y seis commits en GitHub, (4) dos ejecuciones del ETL conectadas a PostgreSQL mostrando conteos iguales. Este PDF incluye métricas calculadas desde archivos y código, no evidencia de ejecución en aplicaciones externas.',styles['Bodyx']),Paragraph('Referencias',styles['H1x'])]
    for i,(title,url) in enumerate(sources,1): story.append(Paragraph(f'[{i}] {title} <link href="{url}" color="#177e89">{url}</link>',styles['Smallx']))
    def footer(canvas,doc):
        canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#71808c')); canvas.drawString(.65*inch,.4*inch,'SolarBI Pascual · Inteligencia de Negocios · Grupo 01'); canvas.drawRightString(7.85*inch,.4*inch,str(doc.page)); canvas.restoreState()
    doc=SimpleDocTemplate(str(PDF),pagesize=letter,rightMargin=.65*inch,leftMargin=.65*inch,topMargin=.6*inch,bottomMargin=.65*inch,title='Consulta SolarBI Pascual - Inteligencia de Negocios')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(PDF)

if __name__=='__main__': build()
