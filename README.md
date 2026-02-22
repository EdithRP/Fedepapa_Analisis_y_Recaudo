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
> * 🖼️ [Visualización de la Ruta de Datos](https://github.com/EdithRP/Fedepapa_Analisis_y_Recaudo/blob/main/img/modeloinicial.png)

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

### Paso 3.2: Creación de Tablas de Dimensión
Para eliminar la redundancia y permitir un análisis temporal y geográfico preciso, se crearon tablas maestras mediante SQL:

* **Dimensión Tiempo (`dim_tiempo`)**: Centraliza la jerarquía de Año, Mes (en español), Semestre y Número de Semana. Es vital para unir la producción mensual con los precios semanales.
* **Dimensión Geografía (`dim_geografia`)**: Unifica los nombres de los departamentos bajo el campo `departamento_normalizado`, resolviendo discrepancias de escritura entre las fuentes originales.


### Paso 3.3: Creación de Tablas de Hechos (Métricas)
Se generaron tablas de hechos (`fct_`) normalizadas que contienen exclusivamente las métricas necesarias para las actividades de la prueba, eliminando columnas de texto redundantes:

* **`fct_precios`**: Registro histórico de precios por variedad y ciudad.
* **`fct_produccion`**: Cifras de producción donde se aplicó la lógica de conversión de Toneladas a Kilogramos.
* **`fct_recaudo`**: Detalle financiero del recaudo real e intereses de mora.

### 💡 Resumen del Proceso de Ingeniería
Se optó por este proceso de **Modelado Dimensional (Star Schema)** en BigQuery por tres razones fundamentales:

1.  **Optimización en Power BI**: Los modelos en estrella son significativamente más rápidos y eficientes para el motor DAX, evitando relaciones de "muchos a muchos".
2.  **Integridad de Datos**: Al centralizar los nombres de meses y departamentos en tablas únicas, se garantiza que no existan inconsistencias al filtrar la información.
3.  **Preparación para el Análisis**: Al realizar la conversión de unidades (Ton a Kg) y la limpieza geográfica en el Warehouse (SQL), se entrega un dato "listo para consumir", cumpliendo con los estándares de un entorno profesional de Ingeniería de Datos.

---

## 🚀 4. Actividades de la Prueba
1. **Actividad 1**: Estimación mensual del recaudo potencial integrando producción y precios.
   
3. **Actividad 2**: Análisis de brechas (Potencial vs Real) y volatilidad.
4. **Actividad 3**: Cálculo de concentración (HHI) y segmentación de recaudadores.
