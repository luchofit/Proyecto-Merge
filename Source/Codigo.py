import pandas as pd
import os 
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

root_dir = Path(".").resolve().parent
filename1 = "Campañas Febrero.xlsx"
filename2 = "Rendimiento de Ventas Febrero.xlsx"
filename3 = "Ventas Febrero.xlsx"

def get_data(filename1,filename2,filename3):
    file_path1 = os.path.join(root_dir, "Data", "Raw", filename1)
    file_path2 = os.path.join(root_dir, "Data", "Raw", filename2)
    file_path3 = os.path.join(root_dir, "Data", "Raw", filename3)
    CampañaFeb_1 = pd.read_excel(file_path1,sheet_name="Conjunto de datos1")
    CampañaFeb_2 = pd.read_excel(file_path1,sheet_name="Conjunto de datos2")
    Rendimiento_Vtas_Febrero1 = pd.read_excel(file_path2,sheet_name="Conjunto de datos1")
    Rendimiento_Vtas_Febrero2 = pd.read_excel(file_path2,sheet_name="Conjunto de datos2")
    Ventas_febrero =  pd.read_excel(file_path3,sheet_name="Hoja1")
    return CampañaFeb_1,CampañaFeb_2,Rendimiento_Vtas_Febrero1,Rendimiento_Vtas_Febrero2,Ventas_febrero

def generate_report(CampañaFeb_1,CampañaFeb_2,Rendimiento_Vtas_Febrero1,Rendimiento_Vtas_Febrero2,Ventas_febrero):
    # Seleccionando solo la columna 'Estatus' de Ventas_febrero
    Ventas_febrero_subset = Ventas_febrero[['Estatus','Clave de Confirmación']]
    # Realizando la fusión basada en los campos relacionados
    Rendimiento_Vtas_Febrero1_processed = pd.merge(Rendimiento_Vtas_Febrero1, Ventas_febrero_subset, how='left', left_on='ID de transacción', right_on='Clave de Confirmación')
    # Asignando "NO ENCONTRADO" a las filas donde no hay coincidencias
    Rendimiento_Vtas_Febrero1_processed['Estatus'] = Rendimiento_Vtas_Febrero1_processed['Estatus'].fillna("NO ENCONTRADO")
    # Eliminar valores duplicados en la columna 'ID de transacción'
    Rendimiento_Vtas_Febrero1_processed.drop_duplicates(subset=['ID de transacción'], inplace=True)
    # Filtrar el DataFrame para incluir solo las ventas efectivas
    ventas_efectivas = Rendimiento_Vtas_Febrero1_processed[Rendimiento_Vtas_Febrero1_processed['Estatus'] == 'Interfaced']
    # Calcular la métrica de precio medio
    ventas_efectivas['Precio Medio'] = ventas_efectivas['Ingresos'] / ventas_efectivas['Cantidad']
    # Calcular el precio medio por 'Fuente/Medio'
    precio_medio_por_fuente = ventas_efectivas.groupby('Fuente/Medio')['Precio Medio'].mean()
    # Crear la tabla dinámica con suma de ingresos por 'Fuente/Medio'
    tabla_pivot = pd.pivot_table(ventas_efectivas, values='Ingresos', index='Fuente/Medio', aggfunc='sum')
    # Agregar la columna de precio medio a la tabla pivote
    tabla_pivot['Precio Medio'] = precio_medio_por_fuente 
    #Resetear index
    tabla_pivot = tabla_pivot.reset_index()   
    # Extraer el mercado y el tipo de campaña de la columna 'Campaña'
    CampañaFeb_1['Mercado'] = CampañaFeb_1['Campaña'].str.split('_').str[0]
    CampañaFeb_1['Tipo de Campaña'] = CampañaFeb_1['Campaña'].str.split('_').str[2]
    # Calcular el número de sesiones para cada mercado y tipo de campaña
    sesiones_por_mercado_y_campaña = CampañaFeb_1.groupby(['Mercado', 'Tipo de Campaña'])['Sesiones'].sum().reset_index()
    # Extraer la estrategia de la columna 'Ad Content'
    CampañaFeb_1['Estrategia'] = CampañaFeb_1['Ad Content'].str.split('_').str[-2]
    # Agrupar los datos por campaña y estrategia y encontrar la estrategia que aportó un mayor número de usuarios para cada campaña
    estrategia_max_usuarios_por_campaña = CampañaFeb_1.groupby(['Campaña', 'Estrategia'])['Usuarios'].max().reset_index()
    # Fusionar los DataFrames en función de la columna de fecha común
    merged_df = pd.merge(CampañaFeb_2, Rendimiento_Vtas_Febrero2, on='Índice de día', how='outer')
    # Renombrar columnas
    merged_df.columns = ['Fecha', 'Usuarios', 'Ingresos']
    # Ordenar por fecha
    merged_df = merged_df.sort_values(by='Fecha')
    return tabla_pivot,sesiones_por_mercado_y_campaña,estrategia_max_usuarios_por_campaña,merged_df

def save_date(tabla_pivot,sesiones_por_mercado_y_campaña,estrategia_max_usuarios_por_campaña,merged_df):
    out_name1 = "tabla_pivot.csv"
    out_path1 = os.path.join(root_dir,"Data","Processed", out_name1)
    tabla_pivot.to_csv(out_path1,mode='w', index=False)
    out_name2 = "sesiones_por_mercado_y_campaña.csv"
    out_path2 = os.path.join(root_dir,"Data","Processed", out_name2)
    sesiones_por_mercado_y_campaña.to_csv(out_path2,mode='w', index=False)
    out_name3 = "estrategia_max_usuarios_por_campaña.csv"
    out_path3 = os.path.join(root_dir,"Data","Processed", out_name3)
    estrategia_max_usuarios_por_campaña.to_csv(out_path3,mode='w', index=False)
    out_name4 = "merged_df.csv"
    out_path4 = os.path.join(root_dir,"Data","Processed", out_name4)
    merged_df.to_csv(out_path4,mode='w', index=False)

def main():
    CampañaFeb_1,CampañaFeb_2,Rendimiento_Vtas_Febrero1,Rendimiento_Vtas_Febrero2,Ventas_febrero = get_data(filename1,filename2,filename3)
    tabla_pivot,sesiones_por_mercado_y_campaña,estrategia_max_usuarios_por_campaña,merged_df = generate_report(CampañaFeb_1,CampañaFeb_2,Rendimiento_Vtas_Febrero1,Rendimiento_Vtas_Febrero2,Ventas_febrero)
    save_date(tabla_pivot,sesiones_por_mercado_y_campaña,estrategia_max_usuarios_por_campaña,merged_df)

if __name__ == "__main__":
    main()

