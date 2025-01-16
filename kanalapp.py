import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def fetch_temperature_from_website():
    """Ruft die aktuelle Temperatur von der Website ab."""
    url = "https://www.gkd.bayern.de/de/fluesse/wassertemperatur/kelheim/augsburg-hochablass-12004002/messwerte"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Fehler werfen, falls Statuscode nicht 200
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Finde die erste Tabellenzeile mit der Temperatur
        tbody = soup.find("tbody")
        if not tbody:
            raise ValueError("Kein <tbody>-Element gefunden.")
        
        row = tbody.find("tr")
        if not row:
            raise ValueError("Keine Tabellenzeile gefunden.")
        
        columns = row.find_all("td")
        if len(columns) < 2:
            raise ValueError("Nicht genügend Spalten in der Tabelle.")
        
        # Extrahiere Temperatur
        temperature = columns[1].get_text(strip=True)
        return float(temperature.replace(",", "."))
    except Exception as e:
        print(f"Fehler beim Abrufen der Temperatur: {e}")
        return None  # Falls ein Fehler auftritt, None zurückgeben

@app.get("/temperature")
def get_temperature():
    """Gibt die aktuelle Temperatur zurück."""
    temperature = fetch_temperature_from_website()
    if temperature is None:
        return {"error": "Temperatur konnte nicht abgerufen werden"}
    return {"temperature": temperature}

# Statische Dateien mounten (hier muss dein HTML-Dokument sein!)
app.mount("/", StaticFiles(directory=".", html=True), name="static")
