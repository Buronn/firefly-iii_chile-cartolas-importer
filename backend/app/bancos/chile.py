import pandas as pd
import re

def cartola_banco_chile_csv(input_path, output_path, year):
    # Cargar el archivo Excel
    df = pd.read_excel(input_path, header=24, usecols="B:G")
    
    # Renombrar las columnas para reflejar los nombres que has mencionado
    df.columns = ['Fecha', 'Descripción', 'Canal o Sucursal', 'Cargos', 'Abonos', 'Saldo']
    if df.iloc[0]['Descripción'] == 'SALDO INICIAL':
        df = df.iloc[1:]
    # Filtrar las filas para eliminar todas desde "SALDO FINAL" en adelante
    df = df[df['Descripción'] != 'SALDO FINAL']
    df = df.dropna(subset=['Fecha'])
    
    # Función para validar y corregir el formato de la fecha
    def validate_and_correct_date(date_str, year):
        if re.match(r'^\d{2}/\d{2}$', date_str):
            return f"{date_str}/{year}"
        return None
    
    # Aplicar la función a la columna 'Fecha'
    df['Fecha'] = df['Fecha'].apply(lambda x: validate_and_correct_date(str(x), year))
    
    # Eliminar filas con fechas inválidas
    df = df.dropna(subset=['Fecha'])
    
    # Función para eliminar el punto y el cero en los valores
    def format_currency(value):
        if pd.isna(value):
            return value
        return str(value).replace('.0', '')
    
    # Aplicar la función a las columnas 'Cargos' y 'Abonos'
    df['Cargos'] = df['Cargos'].apply(format_currency)
    df['Abonos'] = df['Abonos'].apply(format_currency)
    
    # Guardar el DataFrame en un archivo CSV
    df.to_csv(output_path, index=False)