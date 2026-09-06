import { Link } from 'react-router-dom';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { useAlerts } from '../context/AlertContext';
import Hero from '../components/Hero';

export default function DashboardPage() {
  const [savedLocalities, setSavedLocalities] = useLocalStorage('settle_saved_localities', []);
  const [prefs] = useLocalStorage('settle_preferences', null);
  const { alertHistory, clearAlertHistory } = useAlerts();

  const removeLocality = (id) => {
    setSavedLocalities(prev => prev.filter(loc => loc.id !== id));
  };

  return (
    <>
      <Hero
        badge="Dashboard"
        badgeIcon=""
        title="My"
        highlight="settle"
        subtitle="Your saved neighborhoods and search preferences in one place."
      />

      <section className="section">
        
        {/* Saved Search Profile */}
        <div style={{ marginBottom: '4rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Last Search Profile</h2>
          {prefs ? (
            <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Max Budget</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--accent)' }}>₹{prefs.max_rent?.toLocaleString('en-IN') || 'N/A'}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Safety Priority</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>{prefs.safety_weight}/10</div>
              </div>
              <div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Commute Priority</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>{prefs.commute_weight}/10</div>
              </div>
              <div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Workplace Hub</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>{prefs.workplace_id || 'None'}</div>
              </div>
              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
                <Link to="/recommend" className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>Run Matchmaker</Link>
              </div>
            </div>
          ) : (
            <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              You haven't run the AI Matchmaker yet. <Link to="/recommend" style={{ color: 'var(--accent)' }}>Try it now!</Link>
            </div>
          )}
        </div>

        {/* Smart Alerts */}
        {alertHistory && alertHistory.length > 0 && (
          <div style={{ marginBottom: '4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Smart Alerts History</h2>
              <button onClick={clearAlertHistory} className="btn-outline" style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem' }}>Clear All</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {alertHistory.map((alert, idx) => {
                const isCritical = alert.severity === 'critical';
                return (
                  <div key={idx} className="glass-card" style={{ padding: '1rem', borderLeft: `4px solid ${isCritical ? 'var(--danger)' : 'var(--warning)'}` }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                      <div style={{ fontSize: '1.5rem' }}>{isCritical ? '⚠️' : '📈'}</div>
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                          {alert.locality_name}, {alert.city_name}
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                          {alert.message}
                        </div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                          {new Date(alert.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Saved Localities */}
        <div>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span></span> Saved Localities
          </h2>
          
          {savedLocalities.length === 0 ? (
            <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              You haven't saved any localities yet. Browse the <Link to="/explore" style={{ color: 'var(--accent)' }}>Directory</Link> and click the Star icon!
            </div>
          ) : (
            <div className="grid">
              {savedLocalities.map((loc) => (
                <div key={loc.id} className="glass-card animate-fade-in" style={{ padding: '1.5rem', position: 'relative' }}>
                  <button 
                    onClick={() => removeLocality(loc.id)}
                    style={{ 
                      position: 'absolute', top: '1rem', right: '1rem', 
                      background: 'none', border: 'none', color: 'var(--text-muted)', 
                      cursor: 'pointer', fontSize: '1.2rem' 
                    }}
                    title="Remove from saved"
                  >
                    ×
                  </button>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>{loc.name || loc.locality}</h3>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>{loc.city_name}</div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Safety</div>
                      <div style={{ fontWeight: 600 }}>{loc.safety_score}/10</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Avg Rent</div>
                      <div style={{ fontWeight: 600 }}>₹{(loc.avg_rent || loc.predicted_rent)?.toLocaleString('en-IN') || 'N/A'}</div>
                    </div>
                  </div>

                  <Link to={`/city/${loc.city_id}/locality/${loc.id}`} className="btn-outline" style={{ display: 'block', textAlign: 'center', width: '100%' }}>
                    View Details
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

      </section>
    </>
  );
}
