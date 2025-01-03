import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Datei, in der der Zählerstand gespeichert wird
DATA_FILE = "badefrequenz.json"

def load_data():
    """Lädt den Zählerstand aus der JSON-Datei."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"counter": 0}  # Initialer Zählerstand, falls Datei nicht existiert

def save_data(data):
    """Speichert den Zählerstand in die JSON-Datei."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

def reset_counter_if_new_year():
    """Setzt den Zählerstand zurück, falls ein neues Jahr beginnt."""
    today = datetime.now()
    if today.strftime("%d-%m") == "31-12":
        save_data({"counter": 0})  # Zähler zurücksetzen

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
        
        # Extrahiere Temperatur und Zeit
        temperature = columns[1].get_text(strip=True)
        return float(temperature.replace(",", "."))
    except Exception as e:
        print(f"Fehler beim Abrufen der Temperatur: {e}")
        return None  # Falls ein Fehler auftritt, None zurückgeben

@app.get("/temperature")
def get_temperature():
    """Gibt die aktuelle Temperatur zurück."""
    reset_counter_if_new_year()
    temperature = fetch_temperature_from_website()
    if temperature is None:
        return {"error": "Temperatur konnte nicht abgerufen werden"}
    return {"temperature": temperature}

@app.post("/increment")
def increment_counter():
    """Erhöht den allgemeinen Zähler und speichert ihn."""
    data = load_data()
    data["counter"] += 1
    save_data(data)
    return {"counter": data["counter"]}

@app.get("/counter")
def get_counter():
    """Gibt den aktuellen Zählerstand zurück."""
    data = load_data()
    return {"counter": data["counter"]}

# Statische Dateien mounten
app.mount("/", StaticFiles(directory=".", html=True), name="static")
