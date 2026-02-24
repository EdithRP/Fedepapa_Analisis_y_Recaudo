# 🥔 Proyecto de Análisis y Gestión de Recaudo - Fedepapa

Este proyecto presenta una solución integral para la gestión estadística del recaudo de la Cuota de Fomento de la Papa, integrando fuentes de producción, precios de mercado y registros de recaudo real.

---

## 🏗️ 1. Modelamiento Inicial (Capa Conceptual)

En esta fase se realizó una arquitectura de datos preliminar sin aplicar transformaciones. El objetivo fue mapear la estructura cruda (*Raw Data*) para identificar las relaciones potenciales y las columnas críticas para el negocio.

* **Estrategia:** Se definió un modelo que permitiera la trazabilidad desde la producción en campo hasta el recaudo en bancos.
* **Flexibilidad:** El diseño es evolutivo; se estructuró para permitir ajustes en la lógica de negocio (como el cálculo del 1% de fomento) sin comprometer la integridad de la data histórica.

> [!TIP]
> **Recursos de Diseño:**
> * 🔗 [Modelo Relacional Interactivo (dbdiagram.io)](https://dbdiagram.io/d/6999ced5bd82f5fce261dd12)
     ![Visualización de la Ruta de Datos](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/modeloinicial.png)

---

## ⚙️ 2. Proceso de ETL (Python)

Se optó por **Python** para el desarrollo del pipeline de datos. Aunque el volumen actual permitiría el uso de herramientas de hoja de cálculo, se priorizó la **escalabilidad y reproducibilidad**, alineándome con los criterios de evaluación de "Integración y calidad del procesamiento".

### Estructura de Scripts ¨[(`/ETL`)](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/tree/main/ETL)
El flujo principal se gestiona desde el archivo ¨[`limpieza.py`](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/ETL/limpieza.ipynb), el cual coordina tres módulos especializados:

1.  **Carga y Limpieza Técnica:** Estandarización de encabezados y carga de archivos.
2.  **Normalización de Fechas:** Unificación de formatos cronológicos para permitir el cruce de datos semanales (precios) con mensuales (recaudo y producción).
3.  **Normalización Geográfica:** Implementación de la función [`normalizar_departamentos()`](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/ETL/normalizacion_departamento.ipynb), eliminando discrepancias de escritura para garantizar *Joins* precisos.

### Diagnóstico de Calidad (Data Profiling)
Durante el proceso se detectó información faltante en las columnas `latitud` y `longitud` de la base de precios.
* **Criterio de Analisis:** Se decidió **no imputar** estos datos. En esta etapa, el análisis se centra en la agregación departamental y no en la georreferenciación puntual. Mantener la data real evita introducir sesgos artificiales en el modelo estadístico.

---
## 🏗️ 3. Arquitectura de Datos y Modelado en BigQuery

Para garantizar la escalabilidad, se implementó una arquitectura de capas (Staging y Warehouse) en la región `southamerica-west1`.

### Paso 3.1: Ingesta Automática a BigQuery
Se desarrolló un pipeline de carga utilizando la librería `pandas-gbq` y el SDK de Google Cloud. Este proceso garantiza que los datos limpios de la fase anterior se alojen de forma segura en el dataset de Staging.

* **Script de Carga:** [Ver Script de Carga en Python](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/cargar_bigquery.py) 
* **Dataset de Destino:** `sgt_fedepapa`.

### Paso 3.2: Creación de Tablas de Dimensión.
Para eliminar la redundancia y permitir un análisis temporal y geográfico preciso, se crearon tablas maestras mediante SQL:

* **Dimensión Tiempo (`dim_tiempo`)**: Centraliza la jerarquía de Año, Mes (en español), Semestre y Número de Semana. Es vital para unir la producción mensual con los precios semanales. ![dim_tiempo](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/dim_fecha.png)
* **Dimensión Geografía (`dim_geografia`)**: Unifica los nombres de los departamentos bajo el campo `departamento_normalizado`, resolviendo discrepancias de escritura entre las fuentes originales. ![dim_geografia](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/dim_geografia.png)


### Paso 3.3: Creación de Tablas de Hechos (Métricas)
Se generaron tablas de hechos (`fct_`) normalizadas que contienen exclusivamente las métricas necesarias para las actividades de la prueba, eliminando columnas de texto redundantes:

* **`fct_precios`**: Registro histórico de precios por variedad y ciudad. ![fact_precios](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/fact_precios.png)
* **`fct_produccion`**: Cifras de producción donde se aplicó la lógica de conversión de Toneladas a Kilogramos. ![fact_produccion](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/fact_produccion.png)
* **`fct_recaudo`**: Detalle financiero del recaudo real e intereses de mora. ![dim_recaudo](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/fact_recaudo.png)

### 💡 Resumen del Proceso de Ingeniería
Se optó por este proceso de **Modelado Dimensional (Star Schema)** en BigQuery por tres razones fundamentales:

1.  **Optimización en Power BI**: Los modelos en estrella son significativamente más rápidos y eficientes para el motor DAX, evitando relaciones de "muchos a muchos".
2.  **Integridad de Datos**: Al centralizar los nombres de meses y departamentos en tablas únicas, se garantiza que no existan inconsistencias al filtrar la información.
3.  **Preparación para el Análisis**: Al realizar la conversión de unidades (Ton a Kg) y la limpieza geográfica en el Warehouse (SQL), se entrega un dato "listo para consumir", cumpliendo con los estándares de un entorno profesional de Ingeniería de Datos.
   
### Predicción de Precios y Producción
Se desarrolló una consulta avanzada para estimar el valor económico del recaudo potencial. 
* **Lógica SQL:** Se implementaron cálculos de tendencias históricas y proyecciones basadas en la producción departamental.
* **Acceso a la Consulta:** Puedes consultar el script de predicción en el siguiente enlace:
  [🔗 Ver Consulta de Predicción en BigQuery](https://console.cloud.google.com/bigquery?sq=79272127263:ad0ecf4e0e834d75b5a7a91df9e9fc41)
---

## 🚀 ## 📊 Análisis y Actividades (Power BI)

El análisis se dividió en tres ejes fundamentales para responder a las necesidades de la dirección de Fedepapa:

### 1. Brechas entre Recaudo Potencial y Observado
Se evaluó la eficacia del recaudo contrastando lo estimado versus lo efectivamente ingresado al fondo.
* **Hallazgo Crítico:** Se detectó una anomalía en los meses de julio y agosto, donde la incidencia de intereses de mora alcanza picos del **0.8%**, sugiriendo una ventana de riesgo de liquidez estacional.

### 2. Estabilidad y Volatilidad
Para medir la consistencia del recaudo, se implementó el **Coeficiente de Variación (CV)**.
* **Resultado:** El análisis permite diferenciar entre una baja gestión de cobro y una falta de calidad en la información (meses con datos de producción incompletos).

### 3. Concentración del Recaudo (Análisis de Riesgo)
Evaluamos qué tan dependiente es el Fondo de sus principales recaudadores.
* **Índice HHI:** Se obtuvo un valor de **337.18**, lo que clasifica al sistema como **altamente diversificado**. Esto reduce el riesgo sistémico ante el incumplimiento de una sola entidad.
* **Curva de Pareto (80/20):** El Top 10 de recaudadores concentra aproximadamente el **47%** del recaudo total.

---

## 🛠️ Diccionario de Medidas DAX Clave

Para garantizar la precisión estadística, se desarrollaron las siguientes medidas:

* **Índice de Concentración (HHI):** Calcula la atomización del mercado de recaudo.
* **CV Volatilidad:** Mide la dispersión relativa para identificar la estabilidad financiera.
* **% Participación Acumulada:** Lógica para la construcción de la curva de Pareto.

## 📂 Estructura del Reporte

El archivo `.pbix` está organizado en las siguientes hojas:
1. **Dashboard Ejecutivo:** Vista de alto nivel con KPIs de cumplimiento nacional.
2. **Análisis Territorial:** Detalle de brechas por departamento y mes.
3. **Gestión de Recaudadores:** Análisis de concentración, Ranking y HHI.

## 💡 Conclusiones de Negocio
1. **Focalización:** Se recomienda centrar la auditoría en el Top 10 de recaudadores, ya que representan casi la mitad del ingreso del fondo.
2. **Calidad del Dato:** Es imperativo estandarizar el reporte de producción en departamentos menores para eliminar "falsas brechas" en el análisis de eficiencia, debido a que se observa que en algunos departamentos el recaudo es mucho mayor al recaudo Potencial.

