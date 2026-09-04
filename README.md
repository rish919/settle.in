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

### Frontend Architecture
- **React 18:** Component-based UI with custom Hooks.
- **Vite:** High-performance build tooling and Hot Module Replacement (HMR).
- **React Router v6:** Client-side routing and layout management.
- **React-Leaflet:** Interactive geospatial mapping and data visualization.
- **Custom CSS System:** Pure CSS implementation using Design Tokens and Glassmorphism (zero external UI libraries).
- **Web Storage API:** State-agnostic user persistence layer via LocalStorage.

### Backend Engineering
- **Python 3.10+ & FastAPI:** High-performance asynchronous API framework.
- **SQLAlchemy & Pydantic:** Robust Object-Relational Mapping (ORM) and rigorous data validation.
- **APScheduler:** Asynchronous background cron jobs for real-time data polling.
- **Uvicorn:** Lightning-fast ASGI web server.
- **httpx:** Non-blocking, asynchronous HTTP client for external API aggregation.
- **Scikit-Learn:** Time-series forecasting and ML pipeline *(Phase 7)*.

### Database & Infrastructure
- **PostgreSQL 15:** Primary relational database, containerized via Docker.
- **Docker & Docker Compose:** Infrastructure-as-Code for reliable database provisioning.
- **SQLite3:** Lightweight fallback for rapid local development.

### Geospatial & Environmental Data Providers
- **OSRM (Open Source Routing Machine):** Live point-to-point driving durations and route optimization.
- **OpenStreetMap Nominatim:** Real-time location geocoding and address resolution.
- **Overpass API:** Extraction of hyper-local infrastructure metrics (hospitals, schools, supermarkets).
- **Open-Meteo API:** Aggregation of live environmental data and Air Quality Indices (AQI).

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
