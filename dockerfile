# Basis-Image mit Python 3.9
FROM python:3.9

# Arbeitsverzeichnis im Container erstellen
WORKDIR /app

# Kopiere alle Dateien ins Arbeitsverzeichnis
COPY . /app

# Installiere Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Port für die Anwendung freigeben
EXPOSE 8000

# Starte die FastAPI-App mit Uvicorn
CMD ["uvicorn", "kanalapp:app", "--host", "0.0.0.0", "--port", "8000"]
