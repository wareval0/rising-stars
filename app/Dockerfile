# Usa una imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del proyecto al contenedor
COPY . .

# Establece el PYTHONPATH para que reconozca los módulos correctamente
ENV PYTHONPATH=/app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá FastAPI
EXPOSE 8000

# Expone el puerto para el ServerAgent
EXPOSE 4444 

# Ejecuta el ServerAgent y la aplicación FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
