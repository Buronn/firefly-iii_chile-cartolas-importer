import pandas as pd

def cartola_banco_estado_csv(input_path, output_path, year):
    # Leer el archivo de Excel
    excel_data = pd.ExcelFile(input_path)

    # Obtener el nombre de la primera hoja
    first_sheet_name = excel_data.sheet_names[0]
    df = excel_data.parse(first_sheet_name, header=16)

    # Limpiar y formatear el DataFrame
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = ['Fecha', 'Descripción', 'N° Operación', 'Abonos', 'Cargos', 'Saldo']
    df = df.dropna(subset=['Fecha'])

    month_map = {
        'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 'May': '05',
        'Jun': '06', 'Jul': '07', 'Ago': '08', 'Sep': '09', 'Oct': '10',
        'Nov': '11', 'Dic': '12'
    }

    # Función para convertir la fecha al formato dd-mm-yyyy
    def convert_date_properly(date_str):
        if '/' in date_str and '-' not in date_str:
            day, month = date_str.split('/')
            month_num = month_map.get(month)
            if month_num:
                return f"{day.zfill(2)}-{month_num}-{year}"
        return date_str

    df['Fecha'] = df['Fecha'].apply(convert_date_properly)

    def is_valid_date(date_str):
        parts = date_str.split('-')
        return len(parts) == 3 and len(parts[0]) == 2 and len(parts[1]) == 2 and len(parts[2]) == 4

    df = df[df['Fecha'].apply(is_valid_date)]

    # Guardar el DataFrame como un archivo CSV
    df.to_csv(output_path, index=False)

    print(f"Archivo CSV guardado en: {output_path}")