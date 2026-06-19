import boto3
import pandas as pd
import plotly.express as px
import time
import os

REGION = "eu-west-1"
DATABASE = "terremotos_db"
OUTPUT_S3 = "s3://terremotos-datalake/athena-results/"
QUERY = "SELECT id, magnitud, lugar, tiempo, latitud, longitud FROM terremotos_db.terremotos_parquet;"

print("🚀 Conectando con Athena (Módulo de Alta Dirección)...")
athena_client = boto3.client('athena', region_name=REGION)

response = athena_client.start_query_execution(
    QueryString=QUERY,
    QueryExecutionContext={'Database': DATABASE},
    ResultConfiguration={'OutputLocation': OUTPUT_S3}
)
query_id = response['QueryExecutionId']

while True:
    status = athena_client.get_query_execution(QueryExecutionId=query_id)
    state = status['QueryExecution']['Status']['State']
    if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
        break
    time.sleep(1)

if state != 'SUCCEEDED':
    print("❌ Error en Athena")
    exit()

results = athena_client.get_query_results(QueryExecutionId=query_id)
columnas = [col['Name'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
filas = []

for row in results['ResultSet']['Rows'][1:]:
    filas.append([col.get('VarCharValue', None) for col in row['Data']])
    
df = pd.DataFrame(filas, columns=columnas)
df['magnitud'] = pd.to_numeric(df['magnitud'])
df['latitud'] = pd.to_numeric(df['latitud'])
df['longitud'] = pd.to_numeric(df['longitud'])
df['tiempo'] = pd.to_datetime(df['tiempo'])

# Forzar tamaños limpios para el mapa corporativo
df['size_mapa'] = df['magnitud'].apply(lambda x: max(float(x), 0.1) * 3)

# --- 1. MAPA (SE QUEDA EN OSCURO PORQUE TE ENCANTA) ---
fig_mapa = px.scatter_mapbox(
    df, lat="latitud", lon="longitud", hover_name="lugar", 
    size="size_mapa", color="magnitud",
    color_continuous_scale=px.colors.sequential.YlOrRd, zoom=1, height=480
)
fig_mapa.update_layout(
    mapbox=dict(style="carto-darkmatter"),
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
html_mapa = fig_mapa.to_html(full_html=False, include_plotlyjs='cdn')

# --- 2. HISTOGRAMA (Estilo Harvard Editorial: Sintaxis Plotly Nueva) ---
fig_hist = px.histogram(
    df, x="magnitud", nbins=12, 
    color_discrete_sequence=['#2c3e50']
)
fig_hist.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        title=dict(text="Escala de Magnitud (Mww)", font=dict(size=11, color="#4a5568")),
        showgrid=False
    ),
    yaxis=dict(
        title=dict(text="Frecuencia de Eventos", font=dict(size=11, color="#4a5568")),
        showgrid=True, 
        gridcolor="#e2e8f0"
    ),
    margin={"r":10,"t":20,"l":10,"b":30}
)
html_hist = fig_hist.to_html(full_html=False, include_plotlyjs=False)

# --- 3. SERIE TEMPORAL (Línea corporativa delgada: Sintaxis Plotly Nueva) ---
df_hora = df.set_index('tiempo').resample('h').count().reset_index()
fig_linea = px.line(
    df_hora, x="tiempo", y="id", markers=False,
    color_discrete_sequence=['#4a5568']
)
fig_linea.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        title=dict(text="Línea de Tiempo (Por Horas)", font=dict(size=11, color="#4a5568")),
        showgrid=False
    ),
    yaxis=dict(
        title=dict(text="Volumen de Sismos", font=dict(size=11, color="#4a5568")),
        showgrid=True, 
        gridcolor="#e2e8f0"
    ),
    margin={"r":10,"t":20,"l":10,"b":30}
)
html_linea = fig_linea.to_html(full_html=False, include_plotlyjs=False)

# Métricas
total_sismos = len(df)
max_mag = df['magnitud'].max()
peor_lugar = df.loc[df['magnitud'].idxmax(), 'lugar'] if total_sismos > 0 else "N/A"

ruta_final = "/home/cloudshell-user/dashboard_terremotos.html"

# --- PLANTILLA HTML ESTILO HARVARD BUSINESS SCHOOL ---
html_completo = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Análisis Global de Actividad Sísmica</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f7f9fb; font-family: 'Georgia', serif; color: #2d3748; }}
        h1, h2, h3, h5 {{ font-family: 'Arial', sans-serif; font-weight: 700; letter-spacing: -0.5px; }}
        .executive-header {{ border-bottom: 2px solid #a30000; padding-bottom: 12px; margin-bottom: 30px; }}
        .card-report {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 24px; }}
        .card-report-header {{ background: #ffffff; border-bottom: 1px solid #edf2f7; padding: 16px 20px; font-family: 'Arial'; font-size: 0.95rem; text-transform: uppercase; color: #1a202c; letter-spacing: 0.5px; font-weight: 600; }}
        .kpi-box {{ border-right: 1px solid #edf2f7; text-align: center; padding: 10px 0; }}
        .kpi-box:last-child {{ border-right: none; }}
        .kpi-val {{ font-family: 'Arial', sans-serif; font-size: 2.2rem; font-weight: bold; color: #a30000; }} /* Rojo Harvard */
        .kpi-lbl {{ font-size: 0.85rem; color: #718096; text-transform: uppercase; font-family: 'Arial'; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="container py-5">
        
        <div class="executive-header d-flex justify-content-between align-items-end">
            <div>
                <h1 class="display-6 mb-1 text-dark" style="font-weight: 800;">Análisis de Actividad Sísmica Global</h1>
                <p class="text-muted mb-0" style="font-size: 1.1rem; font-style: italic;">Infraestructura de Datos de Producción — Optimización AWS Parquet & Athena</p>
            </div>
            <div class="text-end">
                <span class="badge bg-dark px-3 py-2" style="font-family: Arial; border-radius: 2px; font-weight: 500;">FASE 5 COMPLETA</span>
            </div>
        </div>

        <div class="card-report mb-4">
            <div class="row g-0 py-3">
                <div class="col-md-4 kpi-box">
                    <div class="kpi-val">{total_sismos}</div>
                    <div class="kpi-lbl">Eventos Únicos Registrados</div>
                </div>
                <div class="col-md-4 kpi-box">
                    <div class="kpi-val">{max_mag:.2f}</div>
                    <div class="kpi-lbl">Magnitud Máxima Absoluta</div>
                </div>
                <div class="col-md-4 kpi-box">
                    <div class="kpi-val" style="font-size: 1.25rem; font-family: 'Georgia'; padding: 16px 15px 5px 15px; color:#2d3748;">{peor_lugar}</div>
                    <div class="kpi-lbl">Epicentro de Mayor Impacto</div>
                </div>
            </div>
        </div>

        <div class="card-report">
            <div class="card-report-header">🌍 Distribución Geoespacial y Concentración de Energía Sísmica</div>
            <div class="card-body p-0">
                {html_mapa}
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="card-report">
                    <div class="card-report-header">📊 Distribución de Frecuencias por Escala de Magnitud</div>
                    <div class="card-body">
                        {html_hist}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card-report">
                    <div class="card-report-header">📈 Tendencia Temporal: Densidad de Eventos por Hora</div>
                    <div class="card-body">
                        {html_linea}
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="text-center mt-4 text-muted" style="font-size: 0.85rem; font-family: Arial;">
            Informe Técnico Generado mediante Conector Asíncrono Boto3 en AWS CloudShell. Todos los derechos reservados.
        </footer>
    </div>
</body>
</html>
"""

with open(ruta_final, "w", encoding="utf-8") as f:
    f.write(html_completo)

print(f"🎉 INFORME EJECUTIVO GUARDADO CON ÉXITO") 
