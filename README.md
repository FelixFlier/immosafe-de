# ImmoSafe DE 🏠🌊

**Immobilien-Risikoanalyse für Hochwasser und Naturkatastrophen in Deutschland**

ImmoSafe ist eine Webanwendung, die potenzielle Immobilienkäufer dabei unterstützt, das Risiko von Naturkatastrophen wie Hochwasser für eine bestimmte Adresse in Deutschland zu bewerten.

## Features

- 🔍 **Adresssuche** mit Google Places Autocomplete
- 🗺️ **Interaktive Kartenansicht** zur Visualisierung des Standorts
- 📊 **Risikoanalyse** basierend auf:
  - Höhenlage (Elevation)
  - Historische Niederschlagsdaten
  - Wettervorhersagen
- 🎯 **Risikobewertung** mit klarer visueller Darstellung

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modernes, schnelles Web-Framework
- **Uvicorn** - ASGI Server

### Frontend
- **React 18** - UI Library
- **Vite** - Build Tool & Dev Server
- **Google Maps API** - Karten & Geocoding

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Konfiguration

Erstelle eine `.env` Datei im `frontend` Verzeichnis:

```env
VITE_GOOGLE_MAPS_API_KEY=dein_google_maps_api_key
```

## Starten

### Entwicklungsmodus

```bash
# Im Projektroot
./start_app.sh
```

Oder manuell:

```bash
# Terminal 1 - Backend (Port 8001)
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8001

# Terminal 2 - Frontend (Port 5173)
cd frontend
npm run dev
```

### Zugriff

Öffne http://localhost:5173 im Browser.

## Projektstruktur

```
immosafe_prod/
├── backend/
│   ├── main.py                 # FastAPI App
│   ├── services/
│   │   ├── geo_service.py      # Geocoding & Elevation
│   │   ├── weather_service.py  # Wetterdaten
│   │   └── natural_disaster_service.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React Components
│   │   ├── pages/              # Seiten
│   │   ├── App.jsx             # Haupt-App
│   │   └── main.jsx            # Entry Point
│   ├── index.html
│   └── package.json
├── start_app.sh                # Unified Start Script
└── README.md
```

## Lizenz

MIT License

---

Entwickelt mit ❤️ für sichere Immobilienentscheidungen.
