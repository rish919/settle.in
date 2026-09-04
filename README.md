# settle.in

settle is an Urban Intelligence Platform that helps professionals, families, and students find their ideal neighborhoods across India's major cities. It uses a custom AI Matchmaker that calculates personalized neighborhood recommendations based on real-world infrastructure data, commute times, and local rent economics.

## Features

- **Global Directory:** Browse and filter 120+ neighborhoods across 8 major Indian cities.
- **AI Matchmaker:** Input your workplace location and preferences (Budget, Safety, Commute, Air Quality) to get dynamically ranked neighborhood recommendations.
- **Live Commute API:** Integrates with the OpenStreetMap (OSRM) Routing API to instantly compute driving durations from any neighborhood to your specific workplace in traffic.
- **Granular Livability Metrics:** Neighborhoods are scored using a custom algorithmic weighting of real data (distance to city centers, exact count of hospitals, schools, and supermarkets within a radius).
- **Compare:** Compare metrics side-by-side for up to 3 cities or neighborhoods.
- **My settle:** Securely save your favorite neighborhoods and your last-used Matchmaker profile directly to your device.

## Tech Stack

- **Frontend:** React, Vite, React Router, Leaflet (Maps)
- **Backend:** FastAPI (Python), SQLAlchemy, APScheduler
- **Database:** PostgreSQL (or SQLite for local development)
- **APIs:** 
  - OpenStreetMap Nominatim (Geocoding)
  - OSRM (Routing / Commutes)
  - Open-Meteo (Air Quality)
  - Overpass API (Infrastructure Data Sourcing)

## Project Structure

```
settle/
├── backend/                  # FastAPI Application
│   ├── api/routes/           # API Endpoints
│   ├── data/                 # Seed data and mock data sources
│   ├── models/               # Pydantic schemas and SQLAlchemy models
│   ├── scripts/              # ETL pipelines and scoring algorithms
│   ├── services/             # Core business logic
│   └── main.py               # Application entrypoint
└── frontend/                 # React UI
    ├── src/
    │   ├── api/              # Axios/Fetch clients for backend endpoints
    │   ├── components/       # Reusable UI components
    │   ├── hooks/            # Custom React Hooks
    │   ├── pages/            # View components (Home, Recommend, Explore)
    │   └── App.jsx           # Routing definition
```

## Running Locally

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database and populate seed data:
   ```bash
   python scripts/init_db.py
   ```
5. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:5173` in your browser.
