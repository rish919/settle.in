/**
 * CityDetailPage — Placeholder for individual city detail view.
 *
 * TODO: Implement full city detail with:
 * - All livability metrics
 * - Interactive map
 * - Charts and trends
 * - Neighborhood breakdown
 * - ML predictions
 */
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchCityById } from '../api/cityApi';
import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Utility to create custom SVG marker icons
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="${color}">
             <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
             <circle cx="12" cy="9" r="2.5" fill="var(--bg-card)"/>
           </svg>`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

const defaultIcon = createCustomIcon('var(--accent)');
const goodIcon = createCustomIcon('var(--success)');
const moderateIcon = createCustomIcon('var(--warning)');
const poorIcon = createCustomIcon('var(--danger)');

export default function CityDetailPage() {
  const { cityId } = useParams();
  const navigate = useNavigate();
  const [city, setCity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mapMetric, setMapMetric] = useState('none');

  const getMarkerIcon = (locality) => {
    if (mapMetric === 'none') return defaultIcon;
    
    if (mapMetric === 'air_quality_index') {
      const val = locality.air_quality_index;
      if (!val) return defaultIcon;
      if (val <= 50) return goodIcon;
      if (val <= 100) return moderateIcon;
      return poorIcon;
    }
    
    if (mapMetric === 'safety_score') {
      const val = locality.safety_score;
      if (!val) return defaultIcon;
      if (val >= 8) return goodIcon;
      if (val >= 6) return moderateIcon;
      return poorIcon;
    }
    
    return defaultIcon;
  };

  useEffect(() => {
    async function loadCity() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchCityById(cityId);
        setCity(data);
      } catch (err) {
        setError('City not found or API unavailable.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadCity();
  }, [cityId]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <span className="loading-text">Loading city data…</span>
      </div>
    );
  }

  if (error || !city) {
    return (
      <section className="section" style={{ paddingTop: '4rem' }}>
        <div className="error-banner">{error || 'City not found.'}</div>
        <Link to="/explore" className="btn-primary">← Back to Explore</Link>
      </section>
    );
  }

  return (
    <section className="section" style={{ paddingTop: '3rem' }}>
      <Link to="/explore" style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        ← Back to Explore
      </Link>

      <div style={{ marginTop: '1.5rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.25rem' }}>
          {city.name}
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          {city.state}, {city.country}
          {city.population && ` · Population: ${city.population.toLocaleString('en-IN')}`}
        </p>

        {/* Metrics Grid */}
        <div className="city-grid">
          {[
            { label: 'Safety Score', value: city.safety_score ? `${city.safety_score}/10` : 'N/A' },
            { label: 'Air Quality Index', value: city.air_quality_index ?? 'N/A' },
            { label: 'Average Rent', value: city.avg_rent ? `₹${city.avg_rent.toLocaleString('en-IN')}` : 'N/A' },
            { label: 'Commute Score', value: city.commute_score ? `${city.commute_score}/10` : 'N/A' },
            { label: 'Cost of Living', value: city.cost_of_living_index ? `${city.cost_of_living_index}/10` : 'N/A' },
            { label: 'Healthcare', value: city.healthcare_score ? `${city.healthcare_score}/10` : 'N/A' },
            { label: 'Education', value: city.education_score ? `${city.education_score}/10` : 'N/A' },
          ].map((metric) => (
            <div key={metric.label} className="glass-card" style={{ padding: '1.25rem' }}>
              <div className="stat-label">{metric.label}</div>
              <div className="stat-value" style={{ fontSize: '1.5rem', marginTop: '0.5rem' }}>
                {metric.value}
              </div>
            </div>
          ))}
        </div>

        {/* Localities Section */}
        {city.localities && city.localities.length > 0 && (
          <div style={{ marginTop: '3rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>
              Explore Localities
            </h2>
            <div className="city-grid">
              {city.localities.map((locality, i) => {
                const aqiBadge = locality.air_quality_index <= 50 ? { label: 'Good', className: 'badge-good' } :
                                 locality.air_quality_index <= 100 ? { label: 'Moderate', className: 'badge-moderate' } :
                                 { label: 'Poor', className: 'badge-poor' };
                const staggerClass = i < 8 ? `stagger-${i + 1}` : '';
                
                return (
                  <Link
                    key={locality.id}
                    to={`/city/${city.id}/locality/${locality.id}`}
                    className={`glass-card city-card animate-fade-in ${staggerClass}`}
                    style={{ textDecoration: 'none', color: 'inherit' }}
                  >
                    <div className="city-card-header">
                      <div>
                        <div className="city-card-name">{locality.name}</div>
                      </div>
                      {locality.air_quality_index && (
                        <span className={`city-card-badge ${aqiBadge.className}`}>
                          AQI: {aqiBadge.label}
                        </span>
                      )}
                    </div>
              
                    <div className="city-card-stats">
                      {locality.safety_score != null && (
                        <div className="stat-item">
                          <div className="stat-label">Safety</div>
                          <div className="stat-value">{locality.safety_score}/10</div>
                        </div>
                      )}
                      {locality.avg_rent != null && (
                        <div className="stat-item">
                          <div className="stat-label">Avg Rent</div>
                          <div className="stat-value">₹{locality.avg_rent.toLocaleString('en-IN')}</div>
                        </div>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        )}

        {/* Interactive Map Section */}
        {city.localities && city.localities.length > 0 && (
          <div style={{ marginTop: '3rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Locality Map</h2>
              
              {/* Metric Toggle */}
              <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--bg-input)', padding: '0.25rem', borderRadius: 'var(--radius)' }}>
                {['none', 'safety_score', 'air_quality_index'].map((metric) => (
                  <button
                    key={metric}
                    onClick={() => setMapMetric(metric)}
                    style={{
                      background: mapMetric === metric ? 'var(--bg-card-hover)' : 'transparent',
                      color: mapMetric === metric ? 'var(--text-primary)' : 'var(--text-muted)',
                      border: 'none',
                      padding: '0.375rem 0.75rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      textTransform: 'uppercase',
                      transition: 'all 0.2s'
                    }}
                  >
                    {metric === 'none' ? 'None' : metric === 'safety_score' ? 'Safety' : 'AQI'}
                  </button>
                ))}
              </div>
            </div>

            <MapContainer
              center={[city.lat, city.lng]}
              zoom={11}
              scrollWheelZoom={false}
              style={{ height: '450px', width: '100%', borderRadius: 'var(--radius-lg)' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
              />
              
              {city.localities.map((locality) => (
                <Marker 
                  key={locality.id} 
                  position={[locality.lat, locality.lng]}
                  icon={getMarkerIcon(locality)}
                >
                  <Popup>
                    <div style={{ textAlign: 'center', minWidth: '120px' }}>
                      <strong style={{ fontSize: '1rem', display: 'block', marginBottom: '0.25rem' }}>
                        {locality.name}
                      </strong>
                      
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                        {mapMetric === 'safety_score' && `Safety: ${locality.safety_score}/10`}
                        {mapMetric === 'air_quality_index' && `AQI: ${locality.air_quality_index}`}
                        {mapMetric === 'none' && `Rent: ₹${locality.avg_rent?.toLocaleString('en-IN')}`}
                      </div>

                      <button 
                        onClick={() => navigate(`/city/${city.id}/locality/${locality.id}`)}
                        className="btn-primary"
                        style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', width: '100%' }}
                      >
                        View Details
                      </button>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
            
            {/* Map Legend */}
            {mapMetric !== 'none' && (
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)', justifyContent: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--success)' }}></div>
                  {mapMetric === 'safety_score' ? 'High Safety (8-10)' : 'Good AQI (0-50)'}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--warning)' }}></div>
                  {mapMetric === 'safety_score' ? 'Moderate (6-7.9)' : 'Moderate AQI (51-100)'}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--danger)' }}></div>
                  {mapMetric === 'safety_score' ? 'Low Safety (<6)' : 'Poor AQI (>100)'}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
