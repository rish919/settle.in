/**
 * ExplorePage — Browse and search cities with live API data.
 */
import { useState, useEffect } from 'react';
import Hero from '../components/Hero';
import SearchBar from '../components/SearchBar';
import CityCard from '../components/CityCard';
import { fetchCities } from '../api/cityApi';

export default function ExplorePage() {
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  // Fetch cities from the backend
  const loadCities = async (searchQuery) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCities({ search: searchQuery || undefined });
      setCities(data.cities);
    } catch (err) {
      setError(
        'Unable to connect to the settle API. Make sure the backend is running on port 8000.'
      );
      console.error('Failed to fetch cities:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadCities();
  }, []);

  // Search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      loadCities(search);
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  return (
    <>
      <Hero
        badge="Discover & Compare"
        badgeIcon=""
        title="Explore"
        highlight="Cities"
        subtitle="Browse cities across India and see how they compare on safety, air quality, cost of living, and more."
      />

      <section className="section">
        <SearchBar
          value={search}
          onChange={setSearch}
          placeholder="Search cities by name..."
        />

        {error && (
          <div className="error-banner" id="error-message">
            {error}
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <span className="loading-text">Loading cities…</span>
          </div>
        ) : cities.length === 0 && !error ? (
          <div className="empty-state glass-card">
            <div className="empty-state-icon"></div>
            <h3>No Cities Found</h3>
            <p>Try a different search term.</p>
          </div>
        ) : (
          <div className="city-grid" id="city-grid">
            {cities.map((city, i) => (
              <CityCard key={city.id} city={city} index={i} />
            ))}
          </div>
        )}
      </section>
    </>
  );
}
