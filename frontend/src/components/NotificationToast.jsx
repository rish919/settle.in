import React from 'react';

export default function NotificationToast({ alert, onClose }) {
  if (!alert) return null;

  const isCritical = alert.severity === 'critical';
  
  return (
    <div 
      className={`glass-card animate-fade-in`} 
      style={{
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        width: '350px',
        padding: '1.25rem',
        borderLeft: `4px solid ${isCritical ? 'var(--danger)' : 'var(--warning)'}`,
        zIndex: 9999,
        boxShadow: 'var(--shadow-xl)',
        background: 'rgba(30, 41, 59, 0.95)',
        backdropFilter: 'blur(12px)'
      }}
    >
      <button 
        onClick={onClose}
        style={{
          position: 'absolute', top: '0.5rem', right: '0.5rem',
          background: 'none', border: 'none', color: 'var(--text-muted)',
          cursor: 'pointer', fontSize: '1.2rem'
        }}
      >
        ×
      </button>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '1.2rem' }}>{isCritical ? '⚠️' : '📈'}</span>
        <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-primary)' }}>
          {isCritical ? 'Data Anomaly Detected' : 'Smart Forecast Alert'}
        </h4>
      </div>
      
      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
        <strong style={{ color: 'white' }}>{alert.locality_name}, {alert.city_name}</strong>
      </div>
      
      <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
        {alert.message}
      </p>
    </div>
  );
}
