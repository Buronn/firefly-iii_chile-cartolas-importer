import pdfplumber
import pandas as pd
import re

def cartola_mach_csv(input_path, output_path):
    transactions = []

    # Expresión regular para validar el formato de fecha "dd/mm/yyyy"
    date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')

    # Abrir el archivo PDF con pdfplumber
    with pdfplumber.open(input_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Obtener las posiciones de las líneas horizontales y verticales
            vertical_lines = []
            horizontal_lines = []
            
            headers = [
                page.search('Fecha operación')[0],
                page.search('Descripción')[0],
                page.search('Cambio')[0],
                page.search('Moneda')[0],
                page.search('Egreso')[0],
                page.search('Ingreso')[0]
            ]

            # Definir líneas verticales basadas en las posiciones de los encabezados
            vertical_lines = [
                1,
                headers[0]['x0'],
                headers[1]['x0'] - 5,
                headers[2]['x0'],
                headers[3]['x0'],
                headers[4]['x0'],
                headers[5]['x0'],
                headers[5]['x1'] + 12
            ]

            # Filtrar las líneas horizontales
            horizontal_lines = [line['top'] for line in page.lines if line['orientation'] == 0]
            horizontal_lines.insert(0, headers[0]['top'])
            horizontal_lines.append(page.height)

            # Extraer tabla usando las líneas explícitas
            table = page.extract_table({
                "explicit_vertical_lines": vertical_lines,
                "explicit_horizontal_lines": horizontal_lines,
                "intersection_tolerance": 5,
                "snap_tolerance": 3,
                "join_tolerance": 3,
                "min_words_vertical": 1,
                "min_words_horizontal": 1
            })
            
            if table:
                for row in table:
                    # Filtrar filas basadas en el contenido y la longitud
                    if len(row) >= 6 and row[2] != "Fecha operación" and row[2]:
                        # Separar la fecha y cualquier letra adicional
                        date_parts = row[2].split()
                        date = date_parts[0]
                        extra_description = date_parts[1] if len(date_parts) > 1 else ''
                        
                        if row[3] is not None:
                            description = f"{extra_description}{row[3]}".strip()
                        else:
                            description = f"{extra_description}".strip()
                        cambio, moneda, egreso, ingreso = row[7], row[9], row[11], row[13]

                        # Validar el formato de la fecha
                        if date_pattern.match(date):
                            egreso = egreso if egreso else '0'
                            ingreso = ingreso if ingreso else '0'
                            transactions.append([date, description, cambio, moneda, egreso, ingreso])
                        
    # Crear un DataFrame con las transacciones
    df = pd.DataFrame(transactions, columns=["Fecha operación", "Descripción", "Cambio", "Moneda", "Egreso", "Ingreso"])

    # Función para limpiar y convertir columnas de moneda
    def clean_currency_column(column):
        column = column.str.replace('$', '').str.replace('.', '')
        column = column.replace('', '0')  # Reemplazar cadenas vacías con '0'
        return column.astype(int)

    # Aplicar la función a las columnas 'Egreso' y 'Ingreso'
    df['Egreso'] = clean_currency_column(df['Egreso'])
    df['Ingreso'] = clean_currency_column(df['Ingreso'])

    # Guardar el DataFrame como un archivo CSV
    df.to_csv(output_path, index=False)

    print(f"Archivo CSV guardado en: {output_path}")