from flask import Flask, render_template, request, redirect, url_for
import os
import uuid
import logging
from bancos.estado import cartola_banco_estado_csv
from bancos.mach import cartola_mach_csv
from bancos.santander import cartola_santander_csv
from bancos.chile import cartola_banco_chile_csv
from firefly.api import create_import_load

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token = request.form['token']
        bank = request.form['bank']
        year = request.form.get('year')
        file = request.files['file']

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(app.config['PROCESSED_FOLDER']):
            os.makedirs(app.config['PROCESSED_FOLDER'])

        if file:
            session_id = str(uuid.uuid4())
            input_filename = f"{session_id}.pdf" if bank in ['santander', 'mach'] else f"{session_id}.xlsx"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
            output_filename = f"{session_id}.csv"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            file.save(input_path)

            # Procesar el archivo según el banco seleccionado
            if bank == 'estado':
                cartola_banco_estado_csv(input_path, output_path, year)
            elif bank == 'mach':
                cartola_mach_csv(input_path, output_path)
            elif bank == 'santander':
                cartola_santander_csv(input_path, output_path, year)
            elif bank == 'chile':
                cartola_banco_chile_csv(input_path, output_path, year)
            
            create_import_load(token, bank, output_path, session_id)
            # Eliminar el archivo de entrada
            os.remove(input_path)
            os.remove(output_path)

            # Redirigir a otra página de éxito o mostrar un mensaje
            return redirect(url_for('success'))

    url = os.getenv("FIREFLY_APP_URL")
    return render_template('index.html', url=url)

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
