import os
import pandas as pd
import pandas_gbq
from google.oauth2 import service_account

def cargar_desde_local_a_bigquery(carpeta_datos="data_lista_para_subir", dataset_id="silken-champion-476819-c6.sgt_fedepapa"):
    """
    Lee archivos CSV desde una carpeta local y los sube a Google BigQuery.
    """
    # 1. Archivo de credenciales
    ruta_llave = "ETL/llave_google.json"  # Ajusta la ruta si es necesario
    if not os.path.exists(ruta_llave):
        ruta_llave = "llave_google.json"
        
    credenciales = service_account.Credentials.from_service_account_file(ruta_llave)

    # 2. El ID de tu proyecto
    project_id = "silken-champion-476819-c6"
    
    # 3. Leer cada archivo CSV en la carpeta y subirlo
    for archivo in os.listdir(carpeta_datos):
        if archivo.endswith(".csv"):
            ruta_csv = os.path.join(carpeta_datos, archivo)
            nombre_tabla = archivo.replace(".csv", "")
            
            # Leer el dataframe
            df_final = pd.read_csv(ruta_csv)
            
            # Forzar la columna de fecha a formato datetime si existe
            if 'fecha_normalizada' in df_final.columns:
                df_final['fecha_normalizada'] = pd.to_datetime(df_final['fecha_normalizada']).dt.date
            
            destino_tabla = f"{dataset_id}.{nombre_tabla.lower()}"
            
            print(f"Subiendo {nombre_tabla.upper()} a BigQuery en {destino_tabla}...")
            
            # Sube la tabla con if_exists='replace'
            pandas_gbq.to_gbq(
                dataframe=df_final,
                destination_table=destino_tabla,
                project_id=project_id,
                credentials=credenciales,
                if_exists='replace',
                location='southamerica-west1' # Fuerza a que use la región de Chile
            )
            
            print(f"✅ ¡{nombre_tabla.upper()} guardado con éxito en la nube!")

if __name__ == "__main__":
    cargar_desde_local_a_bigquery(carpeta_datos="ETL/data_lista_para_subir")
