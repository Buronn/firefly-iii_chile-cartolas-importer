import pdfplumber
import pandas as pd

def cartola_santander_csv(input_path, output_path, year):
    transactions = []
    table_settings = {
        "vertical_strategy": "lines_strict",
        "horizontal_strategy": "text",
        "intersection_tolerance": 5,
        "snap_tolerance": 3,
        "join_tolerance": 3,
        "edge_min_length": 3,
    }

    with pdfplumber.open(input_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables(table_settings=table_settings)
            
            for table in tables:
                for row in table:
                    if len(row) == 7:  # Ajuste para este documento específico
                        fecha, sucursal, descripcion, doc_num, cargos, abonos, saldo = row
                        cargos = cargos if cargos else '0'
                        abonos = abonos if abonos else '0'
                        transactions.append([fecha, sucursal, descripcion, doc_num, cargos, abonos, saldo])
    
    df = pd.DataFrame(transactions, columns=["Fecha", "Sucursal", "Descripción", "Nº DCTO", "Cargos", "Abonos", "Saldo"])
    
    # Eliminar filas donde la fecha no cumpla el formato "dd/mm"
    df = df[df['Fecha'].str.match(r'^\d{2}/\d{2}$', na=False)]
    
    # Agregar el año a las fechas
    df['Fecha'] = df['Fecha'] + f'/{year}'

    # Quitar los puntos en Cargos y Abonos
    df['Cargos'] = df['Cargos'].str.replace('.', '')
    df['Abonos'] = df['Abonos'].str.replace('.', '')
    
    # Guardar el DataFrame como un archivo CSV
    df.to_csv(output_path, index=False)
    
    print(f"Archivo CSV guardado en: {output_path}")