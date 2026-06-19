# 🌋 Pipeline de Análisis Sísmico Global — AWS & Athena

Este repositorio contiene el pipeline de datos de extremo a extremo para la ingesta, optimización y visualización de la actividad sísmica global, desarrollado como parte de la entrega práctica del programa.

## 🏗️ Arquitectura del Proyecto

El flujo de datos se divide en las siguientes fases estratégicas:

1. **Ingesta e Infraestructura:** Captura de feeds JSON asíncronos y almacenamiento inicial en un Datalake de Amazon S3.
2. **Fase 5 (Optimización de Costes y Rendimiento):** Transformación del almacenamiento de texto plano (JSON) a formato columnar **Apache Parquet con compresión Snappy** mediante consultas `CTAS` (*Create Table As Select*) en AWS Athena. 
3. **Deduplicación:** Implementación de lógica `DISTINCT id` para depurar registros duplicados procedentes del feed continuo.
4. **Capa de Consumo (BI):** Módulo analítico construido en Python mediante la librería `boto3` para la ejecución asíncrona de consultas en Athena.

## 📊 Dashboard Analítico (Estilo Harvard Editorial)

La interfaz visual ha sido diseñada siguiendo los estándares de diseño de informes ejecutivos y Business Intelligence de alta dirección:
- **KPIs Unificados:** Panel superior limpio con métricas clave (Total de eventos únicos, magnitud máxima registrada y epicentro crítico).
- **Cartografía Geoespacial:** Mapa mundial dinámico con fondo oscuro (*Dark Matter*) para maximizar el contraste de los puntos de calor por magnitud.
- **Gráficos de Tendencia:** Distribución de frecuencias (Histograma) y series temporales por hora con paletas de color de alta fidelidad técnica (Gris Oxford y Grafito), eliminando el ruido visual.

## 🚀 Tecnologías Utilizadas
- **Cloud Infrastructure:** AWS S3, AWS Athena, AWS CloudShell.
- **Language & Libraries:** Python 3.13, Boto3, Pandas, Plotly Express.
- **Frontend Framework:** Bootstrap 5.3 (Cargado vía CDN para máxima ligereza).

## 🔧 Cómo Ejecutar el Módulo de Visualización
1. Asegurarse de tener configuradas las credenciales de AWS en el entorno.
2. Ejecutar el script principal:
   ```bash
   python3 dashboard_interactivo.py
