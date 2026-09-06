import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export default function HistoricalTrendsChart({ data }) {
  const [activeMetric, setActiveMetric] = useState('rent');

  if (!data || data.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>No historical data available.</div>;
  }

  const getMetricConfig = () => {
    switch (activeMetric) {
      case 'rent':
        return {
          key: 'rent',
          color: '#3b82f6', // blue
          name: 'Avg Rent (1BHK, ₹)',
          domain: ['auto', 'auto'],
        };
      case 'aqi':
        return {
          key: 'aqi',
          color: '#f59e0b', // amber
          name: 'AQI Level',
          domain: [0, 'dataMax + 20'],
        };
      case 'crime_rate':
        return {
          key: 'crime_rate',
          color: '#ef4444', // red
          name: 'Safety/Crime Index',
          domain: [0, 10],
        };
      default:
        return { key: 'rent', color: '#3b82f6', name: 'Avg Rent (1BHK, ₹)', domain: ['auto', 'auto'] };
    }
  };

  const config = getMetricConfig();

  // Process data to split actual and forecast, ensuring they connect
  let lastActualValue = null;
  const processedData = data.map((d, i) => {
    const val = d[config.key];
    const isForecast = d.is_forecast;
    
    const point = { month_year: d.month_year, original: val };
    
    if (!isForecast) {
      point.actual = val;
      lastActualValue = val;
    } else {
      // If it's the very first forecast point, we should ideally connect it,
      // but Recharts will break the line if 'actual' is missing.
      // A common trick is to start the forecast with the last actual value.
      point.forecast = val;
    }
    
    // Connect the lines: if this is the first forecast point, set the PREVIOUS point's forecast = actual
    // Actually it's easier to just do it in a second pass
    return point;
  });

  // Second pass to connect the lines
  for (let i = 0; i < processedData.length; i++) {
    if (processedData[i].forecast !== undefined && i > 0 && processedData[i-1].actual !== undefined) {
      processedData[i-1].forecast = processedData[i-1].actual;
      break;
    }
  }

  return (
    <div className="card" style={{ padding: '2rem', marginTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Historical Trends & Forecast</h3>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`btn ${activeMetric === 'rent' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveMetric('rent')}
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          >
            Rent
          </button>
          <button
            className={`btn ${activeMetric === 'aqi' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveMetric('aqi')}
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          >
            Air Quality (AQI)
          </button>
          <button
            className={`btn ${activeMetric === 'crime_rate' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveMetric('crime_rate')}
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          >
            Safety Score
          </button>
        </div>
      </div>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={processedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={config.color} stopOpacity={0.8} />
                <stop offset="95%" stopColor={config.color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-light)" />
            <XAxis
              dataKey="month_year"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              dy={10}
            />
            <YAxis
              domain={config.domain}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              tickFormatter={(value) => activeMetric === 'rent' ? `₹${(value / 1000).toFixed(0)}k` : value}
            />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)', backgroundColor: 'var(--bg-card)' }}
              itemStyle={{ color: 'var(--text-main)', fontWeight: 'bold' }}
              formatter={(value, name) => [value, name === 'forecast' ? `${config.name} (Predicted)` : config.name]}
              labelStyle={{ color: '#9ca3af', marginBottom: '4px' }}
            />
            <Area
              type="monotone"
              dataKey="actual"
              stroke={config.color}
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorMetric)"
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="forecast"
              stroke={config.color}
              strokeWidth={3}
              strokeDasharray="5 5"
              fillOpacity={0.3}
              fill="url(#colorMetric)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
