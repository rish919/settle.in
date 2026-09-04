/**
 * Hero — Reusable hero/banner section with badge, title, and subtitle.
 */
export default function Hero({ badge, badgeIcon, title, highlight, subtitle }) {
  return (
    <section className="hero">
      <div className="hero-inner">
        {badge && (
          <span className="hero-badge">
            {badgeIcon && <span>{badgeIcon}</span>}
            {badge}
          </span>
        )}

        <h1>
          {title}{' '}
          {highlight && <span className="gradient-text">{highlight}</span>}
        </h1>

        {subtitle && (
          <p className="hero-subtitle">{subtitle}</p>
        )}
      </div>
    </section>
  );
}
