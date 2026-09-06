/**
 * LocalityDetailPage — Shows details for a specific locality.
 */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchLocalityById, fetchLocalityHistory } from '../api/cityApi';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import CostOfLivingCalculator from '../components/CostOfLivingCalculator';
import HistoricalTrendsChart from '../components/HistoricalTrendsChart';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Define colors for categories
const CATEGORY_COLORS = {
  hospitals: '#ef4444',     // Red
  schools: '#3b82f6',       // Blue
  supermarkets: '#f59e0b',  // Yellow
  parks: '#10b981',         // Green
};

const CATEGORY_LABELS = {
  hospitals: 'Hospitals',
  schools: 'Schools',
  supermarkets: 'Supermarkets',
  parks: 'Parks',
};

// Utility for creating elegant dot markers
const createDotIcon = (color) => {
  return L.divIcon({
    html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.4);"></div>`,
    className: 'custom-dot-icon',
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    popupAnchor: [0, -9],
  });
};

// Center marker icon (purple ring)
const centerIcon = L.divIcon({
  html: `<div style="background: transparent; border-radius: 50%; width: 24px; height: 24px; border: 3px solid #a855f7; box-shadow: 0 0 15px #a855f7;"></div>`,
  className: 'center-marker',
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12],
});

const ICONS = {
  hospitals: createDotIcon(CATEGORY_COLORS.hospitals),
  schools: createDotIcon(CATEGORY_COLORS.schools),
  supermarkets: createDotIcon(CATEGORY_COLORS.supermarkets),
  parks: createDotIcon(CATEGORY_COLORS.parks),
};

export default function LocalityDetailPage() {
  const { cityId, localityId } = useParams();
  const [locality, setLocality] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilters, setActiveFilters] = useState(new Set(['hospitals', 'schools', 'supermarkets', 'parks']));
  const [savedLocalities, setSavedLocalities] = useLocalStorage('settle_saved_localities', []);

  const toggleFilter = (category) => {
    setActiveFilters(prev => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  useEffect(() => {
    async function loadLocality() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchLocalityById(cityId, localityId);
        setLocality(data);
        const histData = await fetchLocalityHistory(cityId, localityId);
        
        let forecastData = [];
        try {
          const { fetchLocalityForecast } = await import('../api/cityApi');
          forecastData = await fetchLocalityForecast(cityId, localityId);
        } catch (e) {
          console.warn("Forecast data not available", e);
        }
        
        // Merge history and forecast
        // We'll add an `is_forecast` flag so the chart knows how to render it
        const merged = [
          ...histData.map(d => ({ ...d, is_forecast: false })),
          ...forecastData.map(d => ({ 
            month_year: d.month_year, 
            rent: d.forecast_rent, 
            aqi: d.forecast_aqi,
            crime_rate: null, // we don't forecast crime yet
            is_forecast: true 
          }))
        ];
        
        setHistoryData(merged);
      } catch (err) {
        setError('Locality not found or API unavailable.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadLocality();
  }, [cityId, localityId]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <span className="loading-text">Loading locality data…</span>
      </div>
    );
  }

  if (error || !locality) {
    return (
      <section className="section" style={{ paddingTop: '4rem' }}>
        <div className="error-banner">{error || 'Locality not found.'}</div>
        <Link to={`/city/${cityId}`} className="btn-primary">← Back to City</Link>
      </section>
    );
  }

  return (
    <section className="section" style={{ paddingTop: '3rem' }}>
      <Link to={`/city/${cityId}`} style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        ← Back to City
      </Link>

      <div style={{ marginTop: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.25rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: 0 }}>
            {locality.name}
          </h1>
          <button
            onClick={() => {
              const isSaved = savedLocalities.some(s => s.id === locality.id);
              if (isSaved) {
                setSavedLocalities(prev => prev.filter(s => s.id !== locality.id));
              } else {
                setSavedLocalities(prev => [...prev, locality]);
              }
            }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: '1.75rem', color: savedLocalities.some(s => s.id === locality.id) ? 'var(--accent)' : 'var(--text-muted)',
              display: 'flex', alignItems: 'center'
            }}
            title={savedLocalities.some(s => s.id === locality.id) ? "Remove from saved" : "Save to My settle"}
          >
            {savedLocalities.some(s => s.id === locality.id) ? 'Saved' : 'Save'}
          </button>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Neighborhood Profile
        </p>

        {/* Metrics Grid */}
        <div className="city-grid">
          {[
            { label: 'Safety Score', value: locality.safety_score ? `${locality.safety_score}/10` : 'N/A' },
            { label: 'Air Quality Index', value: locality.air_quality_index ?? 'N/A' },
            { label: 'Average Rent (1BHK)', value: locality.avg_rent ? `₹${locality.avg_rent.toLocaleString('en-IN')}` : 'N/A' },
            { label: 'Commute Score', value: locality.commute_score ? `${locality.commute_score}/10` : 'N/A' },
            { label: 'Cost of Living', value: locality.cost_of_living_index ? `${locality.cost_of_living_index}/10` : 'N/A' },
            { label: 'Healthcare', value: locality.healthcare_score ? `${locality.healthcare_score}/10` : 'N/A' },
            { label: 'Education', value: locality.education_score ? `${locality.education_score}/10` : 'N/A' },
          ].map((metric) => (
            <div key={metric.label} className="glass-card" style={{ padding: '1.25rem' }}>
              <div className="stat-label">{metric.label}</div>
              <div className="stat-value" style={{ fontSize: '1.5rem', marginTop: '0.5rem' }}>
                {metric.value}
              </div>
            </div>
          ))}
        </div>

        {/* Nearby Services Section */}
        {locality.nearby_services && (
          <div style={{ marginTop: '4rem' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Nearby Services</h2>

            <div style={{ display: 'grid', gridTemplateColumns: '7fr 3fr', gap: '2rem', alignItems: 'start' }}>
              {/* Map */}
              <div style={{ height: '500px', width: '100%', borderRadius: 'var(--radius)', overflow: 'hidden', border: '1px solid var(--border)' }}>
                <MapContainer
                  center={[locality.lat, locality.lng]}
                  zoom={15}
                  style={{ height: '100%', width: '100%' }}
                  scrollWheelZoom={false}
                >
                  <TileLayer
                    url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  />

                  {/* Locality Center Marker */}
                  <Marker
                    position={[locality.lat, locality.lng]}
                    icon={centerIcon}
                  >
                    <Popup>{locality.name} Center</Popup>
                  </Marker>

                  {/* Services Markers — only show active filter categories */}
                  {Object.entries(locality.nearby_services).map(([category, items]) => (
                    activeFilters.has(category) && items.map((item, idx) => (
                      <Marker
                        key={`${category}-${idx}`}
                        position={[item.lat, item.lng]}
                        icon={ICONS[category]}
                      >
                        <Popup>
                          <strong style={{ color: '#000' }}>{item.name}</strong><br />
                          <span style={{ textTransform: 'capitalize', color: '#666', fontSize: '0.8rem' }}>{category}</span>
                        </Popup>
                      </Marker>
                    ))
                  ))}
                </MapContainer>
              </div>

              {/* Directory Sidebar — clickable categories */}
              <div className="glass-card" style={{ padding: '0', maxHeight: '500px', overflowY: 'auto' }}>
                <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', position: 'sticky', top: 0, background: 'var(--bg-secondary)', zIndex: 1 }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Directory</h3>
                  <p style={{ margin: '0.5rem 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>Click a category to toggle it on the map</p>
                </div>

                <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  {Object.entries(locality.nearby_services).map(([category, items]) => {
                    const isActive = activeFilters.has(category);
                    return (
                      <div key={category}>
                        <button
                          onClick={() => toggleFilter(category)}
                          style={{
                            background: isActive ? `${CATEGORY_COLORS[category]}18` : 'transparent',
                            border: `1.5px solid ${isActive ? CATEGORY_COLORS[category] : 'var(--border)'}`,
                            borderRadius: '8px',
                            padding: '0.6rem 1rem',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.6rem',
                            width: '100%',
                            transition: 'all 0.2s ease',
                            marginBottom: '0.75rem',
                            opacity: isActive ? 1 : 0.5,
                          }}
                        >
                          <span style={{
                            width: '10px', height: '10px', borderRadius: '50%',
                            backgroundColor: CATEGORY_COLORS[category],
                            flexShrink: 0
                          }}></span>
                          <span style={{
                            fontSize: '0.85rem',
                            textTransform: 'uppercase',
                            letterSpacing: '1px',
                            color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                            fontWeight: 600,
                          }}>
                            {CATEGORY_LABELS[category] || category}
                          </span>
                          <span style={{
                            marginLeft: 'auto',
                            fontSize: '0.75rem',
                            color: 'var(--text-muted)',
                            fontWeight: 500,
                          }}>
                            {items.length}
                          </span>
                        </button>

                        {isActive && items.length > 0 && (
                          <ul style={{ listStyle: 'none', padding: '0 0 0 0.5rem', margin: 0, display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                            {items.map((item, idx) => (
                              <li key={idx} style={{ fontSize: '0.9rem', color: 'var(--text-primary)', paddingLeft: '0.5rem', borderLeft: `2px solid ${CATEGORY_COLORS[category]}30` }}>
                                {item.name}
                              </li>
                            ))}
                          </ul>
                        )}

                        {isActive && items.length === 0 && (
                          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic', paddingLeft: '0.5rem' }}>None listed</div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Cost of Living Calculator */}
        <CostOfLivingCalculator locality={locality} />

        {/* Historical Time-Series Trends */}
        {historyData && historyData.length > 0 && (
          <HistoricalTrendsChart data={historyData} />
        )}

      </div>
    </section>
  );
}
