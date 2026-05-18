# ImmoSafe DE 🏠🌊

> A full-stack web app that helps prospective German home-buyers assess flood and natural-disaster risk for any address — before they sign.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) ![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Why this exists

Climate change is making natural-disaster risk a first-class concern for German real estate, but buyers have no easy way to assess it for a specific address. Insurance data is opaque, official flood maps are clunky, and weather forecasts only cover days — not lifetimes of ownership. ImmoSafe gives buyers a clear, address-level risk readout in under 10 seconds.

## ✨ Features

- 🔍 **Address autocomplete** powered by Google Places
- 🗺️ **Interactive map view** showing the property's location and surroundings
- 📊 **Risk analysis** combining:
  - Elevation data (lower-elevation properties = higher flood exposure)
  - Historical precipitation patterns
  - Short-term weather forecasts
- 🎯 **Clear visual risk score** instead of raw numbers

## 🛠 Tech stack

**Backend**
- Python 3.11+
- FastAPI (modern async web framework)
- Uvicorn (ASGI server)

**Frontend**
- React 18
- Vite (build tool + dev server)
- Google Maps API (mapping + geocoding)

## 🏗 Project structure

```
immosafe-de/
├── backend/
│   ├── main.py                          # FastAPI app entry
│   ├── services/
│   │   ├── geo_service.py               # Geocoding & elevation
│   │   ├── weather_service.py           # Weather data
│   │   └── natural_disaster_service.py  # Risk scoring
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                  # React components
│   │   ├── pages/                       # Routed views
│   │   └── App.jsx
│   └── package.json
└── start_app.sh                         # One-command launcher
```

## 🚀 Setup

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend**
```bash
cd frontend
npm install
```

**Configuration** — create `frontend/.env`:
```
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

**Run** (from project root):
```bash
./start_app.sh
```

Or manually:
```bash
# Terminal 1 — Backend (port 8001)
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8001

# Terminal 2 — Frontend (port 5173)
cd frontend && npm run dev
```

Open <http://localhost:5173> in your browser.

## 📊 What I learned (PM perspective)

This was my first end-to-end full-stack project. Lessons that translate to PM work:

- **External data is the moat.** The product's value comes from integrating multiple government and weather APIs — the React UI is just the wrapper. PMs in this space should care about data-source quality, not pixel-pushing.
- **Abstraction levels matter.** Backend services (`geo_service`, `weather_service`, `natural_disaster_service`) are each independently testable. That separation is what makes it possible to swap data sources without rewriting the UI.
- **Risk communication is hard.** Showing "Flood risk: 0.37" means nothing to a buyer. The product's job is to translate that into a decision-useful signal.

## 🗺 Roadmap

- [ ] Add historical flood-incident data (CEDIM, BKG flood maps)
- [ ] Earthquake & subsidence risk modules
- [ ] PDF export for buyers to share with insurance/banks
- [ ] Multi-language support (English first)

## 📝 License

MIT
