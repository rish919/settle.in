/**
 * HomePage — Landing page with hero section and feature highlights.
 */
import { Link } from 'react-router-dom';
import Hero from '../components/Hero';

const features = [
  {
    icon: '',
    title: 'Explore Cities',
    description: 'Browse detailed profiles of cities with safety, air quality, rent, and commute data.',
  },
  {
    icon: '',
    title: 'Compare Areas',
    description: 'Side-by-side comparison of neighborhoods to find your ideal match.',
  },
  {
    icon: '',
    title: 'Interactive Maps',
    description: 'Visualize city data on interactive maps with color-coded insights.',
  },
  {
    icon: '',
    title: 'Smart Recommendations',
    description: 'Get personalized city recommendations based on your preferences.',
  },
  {
    icon: '',
    title: 'Trend Forecasts',
    description: 'ML-powered predictions for crime, pollution, and livability trends.',
  },
  {
    icon: '',
    title: 'Alerts & Notifications',
    description: 'Get notified when conditions change in areas you care about.',
  },
];

export default function HomePage() {
  return (
    <>
      <Hero
        badge="Urban Intelligence Platform"
        badgeIcon=""
        title="Find Your Perfect"
        highlight="City"
        subtitle="Make smarter decisions about where to live. Explore real-world data on safety, air quality, cost of living, and more — all in one place."
      />

      {/* CTA Section */}
      <section className="section" style={{ textAlign: 'center', paddingBottom: '2rem' }}>
        <Link to="/explore" className="btn-primary" id="explore-cta">
           Explore Cities
        </Link>
      </section>

      {/* Features Section */}
      <section className="section">
        <div className="section-header" style={{ textAlign: 'center' }}>
          <h2 className="section-title">What settle Offers</h2>
          <p className="section-subtitle">
            A comprehensive platform for urban intelligence and relocation decisions
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              className={`glass-card feature-card animate-fade-in stagger-${i + 1}`}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
