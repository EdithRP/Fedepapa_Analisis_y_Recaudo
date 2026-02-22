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

Se optó por **Python** para el desarrollo del pipeline de datos. Aunque el volumen actual permitiría el uso de herramientas de hoja de cálculo, se priorizó la **escalabilidad, audibilidad y reproducibilidad**, alineándome con los criterios de evaluación de "Integración y calidad del procesamiento".

### Estructura de Scripts (`/ETL`)
El flujo principal se gestiona desde el archivo `limpieza.py`, el cual coordina tres módulos especializados:

1.  **Carga y Limpieza Técnica:** Estandarización de encabezados y saneamiento de cadenas de texto.
2.  **Normalización de Fechas:** Unificación de formatos cronológicos para permitir el cruce de datos semanales (precios) con mensuales (recaudo y producción).
3.  **Normalización Geográfica:** Implementación de la función `departamentos()`, eliminando discrepancias de escritura para garantizar *Joins* precisos.

### Diagnóstico de Calidad (Data Profiling)
Durante el proceso se detectó información faltante en las columnas `latitud` y `longitud` de la base de precios.
* **Criterio de Analista:** Se decidió **no imputar** estos datos. En esta etapa, el análisis se centra en la agregación departamental y no en la georreferenciación puntual. Mantener la data real evita introducir sesgos artificiales en el modelo estadístico.

---

## ☁️ 3. Arquitectura en la Nube (BigQuery)

Para demostrar el máximo potencial técnico, la información procesada se cargó en **Google BigQuery**. 

* **Capa de Staging (STG):** Los datos limpios de Python aterrizan en tablas de staging que preservan todas las columnas originales.
* **Dimensión de Tiempo Dinámica:** Se implementó una lógica SQL que genera un calendario automático desde la fecha mínima de recaudo hasta el `CURRENT_DATE`, asegurando que el modelo sea autosuficiente para futuros reportes.
* **Capa Semántica (Views):** Los cálculos de brechas y KPIs se realizan mediante vistas SQL, entregando a **Power BI** datos ya transformados para un rendimiento óptimo.
