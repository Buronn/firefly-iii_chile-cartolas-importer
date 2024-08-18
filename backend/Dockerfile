FROM python:3.8-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos de requirements y el proyecto
COPY ./app/requirements.txt .

# Instalar las dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto de los archivos
COPY ./app .

EXPOSE 8080

# CMD tail -f /dev/null
CMD python3 app.py