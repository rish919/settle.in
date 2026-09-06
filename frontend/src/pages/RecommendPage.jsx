import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Hero from '../components/Hero';
import LocationSearchBox from '../components/LocationSearchBox';
import { fetchRecommendations, submitFeedback } from '../api/cityApi';
import { useLocalStorage } from '../hooks/useLocalStorage';

const PRESETS = {
  student: {
    max_rent: 20000,
    safety_weight: 6,
    commute_weight: 8,
    aqi_weight: 4,
  },
  professional: {
    max_rent: 45000,
    safety_weight: 7,
    commute_weight: 9,
    aqi_weight: 6,
  },
  family: {
    max_rent: 75000,
    safety_weight: 10,
    commute_weight: 6,
    aqi_weight: 9,
  }
};



export default function RecommendPage() {
  const navigate = useNavigate();
  
  // State
  const [prefs, setPrefs] = useLocalStorage('settle_preferences', {
    max_rent: 50000,
    safety_weight: 5,
    commute_weight: 5,
    aqi_weight: 5,
    max_commute_mins: 60,
    workplace_lat: null,
    workplace_lng: null,
    workplace_id: '',
  });
  
  const [savedLocalities, setSavedLocalities] = useLocalStorage('settle_saved_localities', []);
  
  const [activePreset, setActivePreset] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [feedbackGiven, setFeedbackGiven] = useState({});

  const handleFeedback = async (localityId, interactionType) => {
    try {
      await submitFeedback({
        locality_id: localityId,
        interaction_type: interactionType,
        context_budget: prefs.max_rent,
        context_commute_weight: prefs.commute_weight
      });
      setFeedbackGiven(prev => ({ ...prev, [`${localityId}-${interactionType}`]: true }));
    } catch (err) {
      console.error("Failed to submit feedback", err);
    }
  };

  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setPrefs(prev => ({ ...prev, [name]: Number(value) }));
    setActivePreset(null); // Clear preset if user manually adjusts
  };



  const applyPreset = (presetKey) => {
    setPrefs(PRESETS[presetKey]);
    setActivePreset(presetKey);
  };

  useEffect(() => {
    const fetchMatches = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchRecommendations(prefs);
        setResults(data);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch recommendations.");
      } finally {
        setLoading(false);
      }
    };
    
    // Simple debounce
    const timeoutId = setTimeout(() => {
      fetchMatches();
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [prefs]);

  return (
    <>
      <Hero
        badge="AI Matchmaker"
        badgeIcon=""
        title="Find Your Ideal"
        highlight="Locality"
        subtitle="Tell us what matters most to you, and we'll find the perfect neighborhood."
      />

      <section className="section" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        
        {/* Left Col: Questionnaire Form */}
        <div className="glass-card animate-fade-in" style={{ padding: '2rem', height: 'fit-content' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Your Preferences</h2>
          
          {/* Presets */}
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Presets</div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button 
                className={`btn-primary ${activePreset === 'student' ? '' : 'btn-outline'}`}
                onClick={() => applyPreset('student')}
                style={activePreset !== 'student' ? { background: 'transparent', color: 'var(--accent)', border: '1px solid var(--accent)' } : {}}
              >Student</button>
              <button 
                className={`btn-primary ${activePreset === 'professional' ? '' : 'btn-outline'}`}
                onClick={() => applyPreset('professional')}
                style={activePreset !== 'professional' ? { background: 'transparent', color: 'var(--accent)', border: '1px solid var(--accent)' } : {}}
              >Professional</button>
              <button 
                className={`btn-primary ${activePreset === 'family' ? '' : 'btn-outline'}`}
                onClick={() => applyPreset('family')}
                style={activePreset !== 'family' ? { background: 'transparent', color: 'var(--accent)', border: '1px solid var(--accent)' } : {}}
              >Family</button>
            </div>
          </div>

          {/* Location Constraints */}
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Workplace / Hub</div>
            <LocationSearchBox 
              placeholder="e.g. Microsoft Outer Ring Road"
              onLocationSelect={(loc) => {
                setPrefs(prev => ({
                  ...prev,
                  workplace_lat: loc.lat,
                  workplace_lng: loc.lng,
                  workplace_id: loc.name // used just to check if selected
                }));
              }}
            />
          </div>

          {/* Sliders */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {/* Budget */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <label style={{ fontWeight: 600 }}>Max Rent (Monthly)</label>
                <span style={{ color: 'var(--accent)', fontWeight: 700 }}>₹{prefs.max_rent.toLocaleString('en-IN')}</span>
              </div>
              <input 
                type="range" 
                name="max_rent"
                min="5000" 
                max="150000" 
                step="5000"
                value={prefs.max_rent}
                onChange={handleSliderChange}
                style={{ width: '100%', accentColor: 'var(--accent)' }}
              />
            </div>

            {/* Safety */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <label style={{ fontWeight: 600 }}>Safety Importance</label>
                <span style={{ color: 'var(--text-muted)' }}>{prefs.safety_weight}/10</span>
              </div>
              <input 
                type="range" 
                name="safety_weight"
                min="1" max="10"
                value={prefs.safety_weight}
                onChange={handleSliderChange}
                style={{ width: '100%', accentColor: 'var(--success)' }}
              />
            </div>

            {/* Max Commute Time (only show if workplace selected) */}
            {prefs.workplace_id && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <label style={{ fontWeight: 600 }}>Max Commute</label>
                  <span style={{ color: 'var(--text-muted)' }}>{prefs.max_commute_mins} mins</span>
                </div>
                <input 
                  type="range" 
                  name="max_commute_mins"
                  min="15" max="120" step="5"
                  value={prefs.max_commute_mins}
                  onChange={handleSliderChange}
                  style={{ width: '100%', accentColor: 'var(--danger)' }}
                />
              </div>
            )}

            {/* Commute */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <label style={{ fontWeight: 600 }}>Commute Convenience</label>
                <span style={{ color: 'var(--text-muted)' }}>{prefs.commute_weight}/10</span>
              </div>
              <input 
                type="range" 
                name="commute_weight"
                min="1" max="10"
                value={prefs.commute_weight}
                onChange={handleSliderChange}
                style={{ width: '100%', accentColor: 'var(--accent-secondary)' }}
              />
            </div>

            {/* AQI */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <label style={{ fontWeight: 600 }}>Air Quality Importance</label>
                <span style={{ color: 'var(--text-muted)' }}>{prefs.aqi_weight}/10</span>
              </div>
              <input 
                type="range" 
                name="aqi_weight"
                min="1" max="10"
                value={prefs.aqi_weight}
                onChange={handleSliderChange}
                style={{ width: '100%', accentColor: 'var(--info, #38bdf8)' }}
              />
            </div>
            
          </div>

          {error && <div className="error-banner" style={{ marginTop: '1rem' }}>{error}</div>}
        </div>

        {/* Right Col: Results */}
        <div>
          {results.length > 0 ? (
            <div>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Top Matches For You</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.map((loc, idx) => (
                  <div key={loc.locality_id} className="glass-card animate-fade-in" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                        <div style={{ 
                          background: idx === 0 ? 'var(--accent)' : 'var(--bg-secondary)', 
                          color: idx === 0 ? 'white' : 'var(--text-muted)',
                          width: '30px', height: '30px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold'
                        }}>
                          #{idx + 1}
                        </div>
                        <h3 style={{ fontSize: '1.25rem', margin: 0 }}>{loc.locality}</h3>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'var(--bg-input)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                          {loc.city_name}
                        </span>
                        
                        {/* Match Percentage Badge */}
                        {loc.final_score !== undefined && (
                          <div style={{ 
                            marginLeft: 'auto', 
                            background: loc.final_score >= 0.80 ? 'var(--success)' : (loc.final_score >= 0.60 ? 'var(--warning)' : 'var(--danger)'),
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            fontWeight: 'bold',
                            display: 'flex',
                            gap: '0.5rem',
                            alignItems: 'center'
                          }}>
                            {Math.round(loc.final_score * 100)}% Match
                            {loc.ml_suitability && (
                              <span style={{ opacity: 0.8, fontWeight: 500, fontSize: '0.7rem', borderLeft: '1px solid rgba(255,255,255,0.3)', paddingLeft: '0.5rem' }}>
                                AI: {Math.round(loc.ml_suitability * 100)}%
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        <div><strong>Rent:</strong> ₹{loc.predicted_rent.toLocaleString('en-IN')}</div>
                        <div><strong>Safety:</strong> {loc.safety_score}/10</div>
                        {loc.predicted_commute_minutes ? (
                          <div style={{ color: 'var(--accent)' }}><strong>Est. Commute:</strong> {loc.predicted_commute_minutes} mins</div>
                        ) : null}
                        <div><strong>AQI:</strong> {loc.air_quality_score}</div>
                      </div>
                      
                      {/* Explanations & Tradeoffs */}
                      <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexDirection: 'column' }}>
                        {loc.reasons && loc.reasons.length > 0 && (
                          <div style={{ padding: '0.75rem', background: 'var(--bg-input)', borderRadius: 'var(--radius)', fontSize: '0.85rem', borderLeft: '3px solid var(--success)' }}>
                            <strong style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Why it's a match:</strong>
                            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                              {loc.reasons.map((exp, i) => (
                                <li key={i} style={{ color: 'var(--success)' }}>✓ {exp}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {loc.tradeoffs && loc.tradeoffs.length > 0 && (
                          <div style={{ padding: '0.75rem', background: 'var(--bg-input)', borderRadius: 'var(--radius)', fontSize: '0.85rem', borderLeft: '3px solid var(--warning)' }}>
                            <strong style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Potential Tradeoffs:</strong>
                            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                              {loc.tradeoffs.map((exp, i) => (
                                <li key={i} style={{ color: 'var(--warning)' }}>✗ {exp}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {loc.is_anomaly && loc.anomaly_alerts && loc.anomaly_alerts.length > 0 && (
                          <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: 'var(--radius)', fontSize: '0.85rem', borderLeft: '3px solid var(--danger)' }}>
                            <strong style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--danger)' }}>⚠️ Data Anomaly Detected:</strong>
                            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                              {loc.anomaly_alerts.map((alert, i) => (
                                <li key={i} style={{ color: 'var(--danger)' }}>{alert}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      
                      {/* User Feedback Loop */}
                      <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Feedback: </span>
                        
                        <button 
                          onClick={() => handleFeedback(loc.locality_id, 'like')}
                          className="btn-outline"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', opacity: feedbackGiven[`${loc.locality_id}-like`] ? 0.5 : 1 }}
                          disabled={feedbackGiven[`${loc.locality_id}-like`]}
                        >👍 Good Fit</button>
                        
                        <button 
                          onClick={() => handleFeedback(loc.locality_id, 'dislike')}
                          className="btn-outline"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', opacity: feedbackGiven[`${loc.locality_id}-dislike`] ? 0.5 : 1 }}
                          disabled={feedbackGiven[`${loc.locality_id}-dislike`]}
                        >👎 Not Interested</button>

                        <button 
                          onClick={() => handleFeedback(loc.locality_id, 'too_expensive')}
                          className="btn-outline"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', opacity: feedbackGiven[`${loc.locality_id}-too_expensive`] ? 0.5 : 1 }}
                          disabled={feedbackGiven[`${loc.locality_id}-too_expensive`]}
                        >💰 Too Expensive</button>

                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'center', marginLeft: '1rem' }}>
                      <button 
                        onClick={() => {
                          const isSaved = savedLocalities.some(s => s.id === loc.locality_id);
                          if (isSaved) {
                            setSavedLocalities(prev => prev.filter(s => s.id !== loc.locality_id));
                          } else {
                            setSavedLocalities(prev => [...prev, { ...loc, id: loc.locality_id, name: loc.locality, avg_rent: loc.predicted_rent }]);
                            handleFeedback(loc.locality_id, 'save');
                          }
                        }}
                        style={{ 
                          background: 'none', border: 'none', cursor: 'pointer', 
                          fontSize: '1.5rem', color: savedLocalities.some(s => s.id === loc.locality_id) ? 'var(--accent)' : 'var(--text-muted)',
                          padding: '0.5rem'
                        }}
                        title={savedLocalities.some(s => s.id === loc.locality_id) ? "Remove from saved" : "Save to My settle"}
                      >
                        {savedLocalities.some(s => s.id === loc.locality_id) ? 'Saved' : 'Save'}
                      </button>
                      <button 
                        onClick={() => navigate(`/city/${loc.city_id}/locality/${loc.locality_id}`)}
                        className="btn-primary"
                        style={{ padding: '0.5rem 1rem' }}
                      >
                        View
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="glass-card" style={{ padding: '4rem 2rem', textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}></div>
              <h3 style={{ marginBottom: '0.5rem' }}>No recommendations yet</h3>
              <p style={{ color: 'var(--text-muted)' }}>Loading recommendations...</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
