/**
 * Layout — Wraps all pages with navbar and footer.
 */
import { Link, useLocation } from 'react-router-dom';

const navLinks = [
  { path: '/', label: 'Home' },
  { path: '/explore', label: 'Explore' },
  { path: '/compare', label: 'Compare' },
  { path: '/recommend', label: 'Find Ideal Locality' },
  { path: '/dashboard', label: 'My settle' },
];

export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div className="app-wrapper">
      {/* Navbar */}
      <nav className="navbar" id="main-nav">
        <div className="navbar-inner">
          <Link to="/" className="navbar-brand">
            <span className="navbar-logo"></span>
            settle
          </Link>

          <div className="navbar-links">
            {navLinks.map(({ path, label }) => (
              <Link
                key={path}
                to={path}
                className={`nav-link ${location.pathname === path ? 'active' : ''}`}
                id={`nav-${label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main className="main-content">
        {children}
      </main>

      {/* Footer */}
      <footer className="footer">
         {new Date().getFullYear()} settle — Urban Intelligence Platform
      </footer>
    </div>
  );
}
