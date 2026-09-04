/**
 * ComparePage — Allows side-by-side comparison of cities or localities.
 */
import { useState, useEffect } from 'react';
import Hero from '../components/Hero';
import { fetchCities, fetchComparison } from '../api/cityApi';

// Helper to determine who wins a metric comparison
const getWinner = (val1, val2, metric) => {
  if (val1 == null || val2 == null) return null;
  // Lower is better for AQI and Rent
  if (metric === 'air_quality_index' || metric === 'avg_rent') {
    return val1 < val2 ? 1 : val2 < val1 ? 2 : 0; // 0 is tie
  }
  // Higher is better for others (Safety, Commute, etc.)
  return val1 > val2 ? 1 : val2 > val1 ? 2 : 0;
};

// Metric configuration
const METRICS = [
  { key: 'safety_score', label: 'Safety Score (out of 10)' },
  { key: 'air_quality_index', label: 'Air Quality Index' },
  { key: 'avg_rent', label: 'Average Rent (₹)' },
  { key: 'commute_score', label: 'Commute Score (out of 10)' },
  { key: 'cost_of_living_index', label: 'Cost of Living (out of 10)' },
  { key: 'healthcare_score', label: 'Healthcare (out of 10)' },
  { key: 'education_score', label: 'Education (out of 10)' }
];

export default function ComparePage() {
  const [compareType, setCompareType] = useState('city');
  const [citiesData, setCitiesData] = useState([]);
  
  // Selections
  const [city1, setCity1] = useState('');
  const [city2, setCity2] = useState('');
  const [locality1, setLocality1] = useState('');
  const [locality2, setLocality2] = useState('');
  
  // Results
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  // Fetch baseline city data for dropdowns on mount
  useEffect(() => {
    async function init() {
      try {
        const data = await fetchCities();
        setCitiesData(data.cities);
      } catch (err) {
        console.error("Failed to fetch cities list", err);
      }
    }
    init();
  }, []);

  const handleCompare = async () => {
    setError(null);
    setResults(null);

    // Validation
    if (compareType === 'city' && (!city1 || !city2)) {
      return setError('Please select two cities to compare.');
    }
    if (compareType === 'locality' && (!city1 || !city2 || !locality1 || !locality2)) {
      return setError('Please select two localities to compare.');
    }

    setLoading(true);
    try {
      if (compareType === 'city') {
        const data = await fetchComparison('city', city1, city2);
        setResults(data);
      } else {
        const data = await fetchComparison('locality', locality1, locality2, city1, city2);
        setResults(data);
      }
    } catch (err) {
      setError('Comparison failed. Ensure you selected valid locations.');
    } finally {
      setLoading(false);
    }
  };

  // Helper to render dropdown options for localities
  const renderLocalityOptions = (selectedCityId) => {
    const city = citiesData.find(c => c.id === selectedCityId);
    if (!city || !city.localities) return <option value="">No localities available</option>;
    return (
      <>
        <option value="">Select Locality</option>
        {city.localities.map(loc => (
          <option key={loc.id} value={loc.id}>{loc.name}</option>
        ))}
      </>
    );
  };

  return (
    <>
      <Hero
        badge="Hierarchical Comparison"
        badgeIcon=""
        title="Compare"
        highlight="Locations"
        subtitle="Place cities or specific neighborhoods side-by-side to see how they stack up."
      />

      <section className="section">
        {/* Toggle & Selection Form */}
        <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
          
          {/* Type Toggle */}
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', justifyContent: 'center' }}>
            <button
              onClick={() => { setCompareType('city'); setResults(null); }}
              className={compareType === 'city' ? 'btn-primary' : 'nav-link'}
              style={{ border: compareType === 'city' ? 'none' : '1px solid var(--border)' }}
            >
              Compare Cities
            </button>
            <button
              onClick={() => { setCompareType('locality'); setResults(null); }}
              className={compareType === 'locality' ? 'btn-primary' : 'nav-link'}
              style={{ border: compareType === 'locality' ? 'none' : '1px solid var(--border)' }}
            >
              Compare Localities
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Location 1 Selector */}
            <div>
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Location A</h3>
              <select 
                className="search-bar" 
                value={city1} 
                onChange={(e) => { setCity1(e.target.value); setLocality1(''); }}
                style={{ marginBottom: compareType === 'locality' ? '1rem' : '0' }}
              >
                <option value="">Select City</option>
                {citiesData.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              
              {compareType === 'locality' && (
                <select 
                  className="search-bar" 
                  value={locality1} 
                  onChange={(e) => setLocality1(e.target.value)}
                  disabled={!city1}
                >
                  {city1 ? renderLocalityOptions(city1) : <option value="">Select City First</option>}
                </select>
              )}
            </div>

            {/* Location 2 Selector */}
            <div>
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Location B</h3>
              <select 
                className="search-bar" 
                value={city2} 
                onChange={(e) => { setCity2(e.target.value); setLocality2(''); }}
                style={{ marginBottom: compareType === 'locality' ? '1rem' : '0' }}
              >
                <option value="">Select City</option>
                {citiesData.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              
              {compareType === 'locality' && (
                <select 
                  className="search-bar" 
                  value={locality2} 
                  onChange={(e) => setLocality2(e.target.value)}
                  disabled={!city2}
                >
                  {city2 ? renderLocalityOptions(city2) : <option value="">Select City First</option>}
                </select>
              )}
            </div>
          </div>

          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <button onClick={handleCompare} className="btn-primary" disabled={loading}>
              {loading ? 'Loading...' : 'Compare Locations'}
            </button>
            {error && <div className="error-banner" style={{ marginTop: '1rem' }}>{error}</div>}
          </div>
        </div>

        {/* Results Section */}
        {results && (
          <div className="glass-card animate-fade-in" style={{ padding: '2rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr', gap: '1rem', marginBottom: '2rem', textAlign: 'center' }}>
              <h2 style={{ fontSize: '1.75rem', color: 'var(--accent)' }}>{results.location1.name}</h2>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>VS</div>
              <h2 style={{ fontSize: '1.75rem', color: 'var(--accent-secondary)' }}>{results.location2.name}</h2>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {METRICS.map(metric => {
                const val1 = results.location1[metric.key];
                const val2 = results.location2[metric.key];
                const winner = getWinner(val1, val2, metric.key);
                
                // Format display values
                const disp1 = val1 == null ? 'N/A' : metric.key === 'avg_rent' ? `₹${val1.toLocaleString('en-IN')}` : val1;
                const disp2 = val2 == null ? 'N/A' : metric.key === 'avg_rent' ? `₹${val2.toLocaleString('en-IN')}` : val2;

                return (
                  <div key={metric.key} style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: 'var(--radius)' }}>
                    <div style={{ textAlign: 'center', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                      {metric.label}
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: '1rem' }}>
                      {/* Left Side (Location 1) */}
                      <div style={{ 
                        textAlign: 'right', 
                        fontSize: '1.25rem', 
                        fontWeight: winner === 1 ? 800 : 500,
                        color: winner === 1 ? 'var(--success)' : (winner === 2 ? 'var(--text-muted)' : 'var(--text-primary)') 
                      }}>
                        {disp1} {winner === 1 && ''}
                      </div>
                      
                      {/* Center Bar Placeholder */}
                      <div style={{ width: '2px', height: '30px', background: 'var(--border)' }}></div>
                      
                      {/* Right Side (Location 2) */}
                      <div style={{ 
                        textAlign: 'left', 
                        fontSize: '1.25rem', 
                        fontWeight: winner === 2 ? 800 : 500,
                        color: winner === 2 ? 'var(--success)' : (winner === 1 ? 'var(--text-muted)' : 'var(--text-primary)') 
                      }}>
                        {winner === 2 && ''} {disp2}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </section>
    </>
  );
}
