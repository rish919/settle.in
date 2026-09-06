/**
 * CityCard — Displays a city with its key livability metrics.
 */
import { Link } from 'react-router-dom';

/**
 * Get AQI badge info based on the air quality index value.
 */
function getAqiBadge(aqi) {
  if (aqi <= 50) return { label: 'Good', className: 'badge-good' };
  if (aqi <= 100) return { label: 'Moderate', className: 'badge-moderate' };
  if (aqi <= 200) return { label: 'Poor', className: 'badge-poor' };
  return { label: 'Severe', className: 'badge-severe' };
}

export default function CityCard({ city, index }) {
  const aqiBadge = city.air_quality_index ? getAqiBadge(city.air_quality_index) : null;

  // Stagger animation class (capped at 8)
  const staggerClass = index < 8 ? `stagger-${index + 1}` : '';

  return (
    <Link
      to={`/city/${city.id}`}
      className={`glass-card city-card animate-fade-in ${staggerClass}`}
      id={`city-card-${city.id}`}
      style={{ textDecoration: 'none', color: 'inherit' }}
    >
      <div className="city-card-header">
        <div>
          <div className="city-card-name">{city.name}</div>
          <div className="city-card-location">{city.state}, {city.country}</div>
        </div>
        {aqiBadge && (
          <span className={`city-card-badge ${aqiBadge.className}`}>
            AQI: {aqiBadge.label}
          </span>
        )}
      </div>

      <div className="city-card-stats">
        {city.safety_score != null && (
          <div className="stat-item">
            <div className="stat-label">Safety</div>
            <div className="stat-value">{city.safety_score}/10</div>
          </div>
        )}
        {city.avg_rent != null && (
          <div className="stat-item">
            <div className="stat-label">Avg Rent (1BHK)</div>
            <div className="stat-value">₹{city.avg_rent.toLocaleString('en-IN')}</div>
          </div>
        )}
        {city.air_quality_index != null && (
          <div className="stat-item">
            <div className="stat-label">Air Quality</div>
            <div className="stat-value">AQI {city.air_quality_index}</div>
          </div>
        )}
        {city.commute_score != null && (
          <div className="stat-item">
            <div className="stat-label">Commute</div>
            <div className="stat-value">{city.commute_score}/10</div>
          </div>
        )}
      </div>
    </Link>
  );
}
