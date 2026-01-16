# ImmoSafe DE 🏠🌊

**Umfassende Naturkatastrophen-Risikoanalyse für deutsche Immobilien**

ImmoSafe ist eine production-ready Webanwendung, die potenzielle Immobilienkäufer dabei unterstützt, das Risiko von Naturkatastrophen für eine bestimmte Adresse in Deutschland zu bewerten.

## Features

### Hauptfunktionen
- 🔍 **Intelligente Adresssuche** mit Google Places Autocomplete
- 🗺️ **Interaktive Kartenansicht** zur Visualisierung des Standorts
- 📊 **Umfassende Risikoanalyse** für 6 Naturkatastrophen-Typen:
  - 🌊 **Hochwasser** - Basierend auf Elevation, historischen Niederschlägen und Geländeanalyse
  - 💨 **Sturm** - Windgeschwindigkeiten und Sturmhäufigkeit
  - 🔥 **Waldbrand** - Temperaturen, Trockenheit und Niederschlagsdefizite
  - 🌡️ **Extremtemperaturen** - Hitze- und Kältewellen
  - 🧊 **Hagel** - Hagelereignisse und Niederschlagsintensität
  - 🏚️ **Erdbeben** - Erdbebenzoneneinteilung nach DIN EN 1998-1
- 🎯 **Detaillierte Risikobewertung** mit visuellen Darstellungen
- 📈 **Wetterdaten & Prognosen** - Historische Analyse und 3-Tage-Vorhersage
- ⚡ **Performance-optimiert** mit Multi-Level-Caching (TTL: 30-60 Minuten)
- 🔒 **Production-ready** mit CORS-Schutz, Rate Limiting und strukturiertem Logging

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

### Backend Environment Variables

Erstelle eine `.env` Datei im **Projekt-Root** basierend auf `.env.example`:

```bash
cp .env.example .env
```

Erforderliche Variablen:
```env
# REQUIRED
MAPS_API_KEY=your_google_maps_api_key_here

# OPTIONAL (Production-Settings)
ALLOWED_ORIGINS=https://yourdomain.com
DEBUG=false
```

### Frontend Environment Variables

Erstelle eine `.env` Datei im `frontend` Verzeichnis:

```env
VITE_GOOGLE_MAPS_API_KEY=dein_google_maps_api_key
```

### Google Maps API Setup

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Erstelle ein neues Projekt oder wähle ein bestehendes aus
3. Aktiviere folgende APIs:
   - **Geocoding API**
   - **Elevation API**
   - **Maps JavaScript API** (für Frontend)
   - **Places API** (für Autocomplete)
4. Erstelle einen API Key
5. **Wichtig für Production:** Beschränke den API Key auf:
   - Bestimmte APIs
   - HTTP-Referrer (für Frontend-Key)
   - IP-Adressen (für Backend-Key)

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

## Production Deployment

### Backend Deployment

**Empfohlene Plattformen:**
- **Render** (einfach, managed)
- **Railway** (managed)
- **DigitalOcean App Platform**
- **AWS Elastic Beanstalk**
- **Google Cloud Run**

**Deployment-Schritte:**

1. **Setze Environment-Variablen:**
   ```env
   MAPS_API_KEY=your_key
   ALLOWED_ORIGINS=https://yourdomain.com
   DEBUG=false
   ```

2. **Installiere Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Starte den Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
   ```

4. **Health Check:** `GET /health`

### Frontend Deployment

**Empfohlene Plattformen:**
- **Vercel** (empfohlen für React)
- **Netlify**
- **Cloudflare Pages**

**Build-Befehl:**
```bash
cd frontend
npm run build
```

**Environment-Variablen setzen:**
```env
VITE_GOOGLE_MAPS_API_KEY=your_frontend_key
```

**Output-Verzeichnis:** `frontend/dist`

### CORS-Konfiguration

Nach dem Deployment:
1. Notiere die Frontend-URL (z.B. `https://immosafe.vercel.app`)
2. Setze `ALLOWED_ORIGINS` im Backend auf diese URL
3. Restart Backend

### Monitoring & Logging

Das Backend loggt automatisch:
- Alle eingehenden Requests mit Timing
- Fehler mit vollständigem Stack Trace
- Cache-Hits/-Misses
- API-Aufrufe zu externen Services

**Logs ansehen:**
```bash
# Bei lokaler Entwicklung
tail -f logs/app.log

# Bei Cloud-Deployments: Platform-spezifische Log-Viewer nutzen
```

## Projektstruktur

```
immosafe-de/
├── backend/
│   ├── main.py                 # FastAPI App & Endpoints
│   ├── services/
│   │   ├── external_api.py     # Google Maps & Open-Meteo APIs
│   │   ├── risk_calculator.py  # Hochwasser-Risiko-Algorithmus
│   │   └── natural_disaster_service.py  # 6 Naturkatastrophen-Analysen
│   └── requirements.txt        # Python Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── landing/        # Landing Page Components
│   │   │   ├── ComprehensiveRiskCard.jsx  # Hauptanalyse-Anzeige
│   │   │   ├── RiskOverview.jsx
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── package.json
├── .env.example                # Environment-Variablen Template
├── start_app.sh                # Unified Start Script
└── README.md
```

## API Dokumentation

### POST /api/analyze
Führt eine umfassende Naturkatastrophen-Analyse durch.

**Request Body:**
```json
{
  "address": "Marienplatz 1, 80331 München, Deutschland"
}
```

**Response:**
```json
{
  "address": "string",
  "coordinates": {"lat": 48.137, "lng": 11.575},
  "total_risk_score": 42,
  "total_risk_level": "Medium",
  "primary_risks": ["Hochwasser", "Sturm"],
  "flood_risk": {...},
  "storm_risk": {...},
  "fire_risk": {...},
  "temperature_risk": {...},
  "hail_risk": {...},
  "earthquake_risk": {...}
}
```

**Rate Limit:** 10 Requests/Minute pro IP

### GET /health
Health Check mit API-Key-Status.

## Technische Details

### Caching-Strategie
- **TTL:** 30-60 Minuten (je nach Datentyp)
- **Max Size:** 500-1000 Einträge pro Cache
- **Cache-Keys:** Koordinaten (gerundet auf 4 Dezimalstellen)
- **Implementierung:** `cachetools.TTLCache`

### Externe APIs
- **Google Maps APIs** (Geocoding, Elevation) - Kostenpflichtig, $200/Monat Free Tier
- **Open-Meteo** (Wetter & Klima) - Kostenlos, keine API-Key erforderlich

### Performance
- Parallel API-Aufrufe (asyncio)
- Multi-Level-Caching
- Graceful degradation bei API-Fehlern
- Response-Zeit: ~500-1500ms (ohne Cache), ~50-100ms (mit Cache)

## Sicherheit

- ✅ CORS-Schutz (konfigurierbar)
- ✅ Rate Limiting (10 req/min)
- ✅ Input-Validierung mit Pydantic
- ✅ Kein hardcoded Secrets
- ✅ Environment-basierte Konfiguration
- ⚠️ Authentifizierung nicht implementiert (geplant für v3.0)

## 🚀 Launch-Checkliste

### Pre-Launch (Lokal testen)
- [ ] Backend-Dependencies installieren: `cd backend && pip install -r requirements.txt`
- [ ] Frontend-Dependencies installieren: `cd frontend && npm install`
- [ ] `.env` Dateien konfigurieren (siehe Konfiguration-Sektion)
- [ ] App lokal starten: `./start_app.sh`
- [ ] PDF-Export testen: Dashboard → Analyse durchführen → PDF-Button klicken
- [ ] SEO testen: Browser DevTools → Head-Tags überprüfen

### Backend-Deployment
- [ ] **Plattform wählen**: Render / Railway / DigitalOcean
- [ ] Environment-Variablen setzen:
  - `MAPS_API_KEY=your_key`
  - `ALLOWED_ORIGINS=https://your-frontend-domain.com`
  - `DEBUG=false`
- [ ] Deployment durchführen
- [ ] Health-Check testen: `GET https://your-backend.com/health`
- [ ] API testen: `POST https://your-backend.com/api/analyze` mit Test-Adresse

### Frontend-Deployment
- [ ] **Plattform wählen**: Vercel (empfohlen) / Netlify / Cloudflare Pages
- [ ] Environment-Variablen setzen:
  - `VITE_GOOGLE_MAPS_API_KEY=your_frontend_key`
- [ ] Build-Command: `npm run build`
- [ ] Output-Directory: `dist`
- [ ] Deployment durchführen
- [ ] Domain notieren (z.B. `https://immosafe.vercel.app`)

### Post-Deployment Konfiguration
- [ ] Backend `ALLOWED_ORIGINS` aktualisieren mit Frontend-URL
- [ ] Backend neu starten
- [ ] CORS-Test: Frontend → API-Aufruf sollte funktionieren
- [ ] Vollständige User-Journey testen:
  - Adresse eingeben
  - Analyse durchführen
  - Alle Tabs überprüfen (Übersicht, Kategorien, Premium Insights, Wetterdaten)
  - PDF herunterladen
  - Teilen/Link-Funktionalität

### SEO & Marketing
- [ ] `sitemap.xml` mit echter Domain aktualisieren:
  - Datei: `frontend/public/sitemap.xml`
  - Ersetze `https://immosafe.de` mit deiner Domain
- [ ] `robots.txt` mit echter Domain aktualisieren (optional)
- [ ] [Google Search Console](https://search.google.com/search-console) einrichten
  - Domain verifizieren
  - Sitemap submitten
- [ ] [Google Analytics](https://analytics.google.com) einrichten (optional)
- [ ] Social Media Images erstellen:
  - OG-Image: 1200x630px
  - Twitter Card: 1200x600px
  - Speichern als `/frontend/public/og-image.png`

### Monitoring & Analytics
- [ ] Error-Tracking einrichten (z.B. Sentry)
- [ ] API-Usage überwachen (Google Maps Quota)
- [ ] Performance-Monitoring (Vercel Analytics / Plausible)

### Optional: Custom Domain
- [ ] Domain kaufen (z.B. immosafe.de bei Namecheap/GoDaddy)
- [ ] DNS konfigurieren:
  - A-Record für Backend
  - CNAME für Frontend (Vercel/Netlify)
- [ ] SSL-Zertifikat (meist automatisch)

## Bekannte Einschränkungen

- Keine Benutzer-Authentifizierung (für Testing-Launch nicht erforderlich)
- In-Memory-Caching (nicht persistent, reicht für Testing)
- Keine Datenbank für Audit-Trails (für v2.0 geplant)

## Roadmap

- [ ] Benutzer-Authentifizierung & Premium-Accounts
- [ ] PDF-Report-Generation
- [ ] Persistent Caching (Redis)
- [ ] Datenbank für Analyse-Historie
- [ ] API-Rate-Limiting pro Benutzer
- [ ] Erweiterte Erdbeben-Daten (Echtzeit-Feeds)

## Lizenz

MIT License

---

**Entwickelt mit ❤️ für sichere Immobilienentscheidungen.**

*Version 2.0.0 - Production Ready*
