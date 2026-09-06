import { useState, useEffect } from 'react';

export default function CostOfLivingCalculator({ locality }) {
  // Default salary to 1,00,000
  const [salary, setSalary] = useState(100000);
  
  // Calculate a baseline lifestyle expense: ₹15,000 scaled by the cost of living index (1-10)
  const colIndex = locality.cost_of_living_index || 5;
  const initialExpenses = Math.round(15000 * (colIndex / 5));
  const [lifestyleExpenses, setLifestyleExpenses] = useState(initialExpenses);

  const rent = locality.avg_rent || 0;
  const totalExpenses = rent + lifestyleExpenses;
  const savings = salary - totalExpenses;
  
  // Calculate percentages for the segmented bar
  // If total > salary, we scale everything to total expenses so the bar is full
  const maxBarValue = Math.max(salary, totalExpenses);
  
  const rentPct = (rent / maxBarValue) * 100;
  const expensesPct = (lifestyleExpenses / maxBarValue) * 100;
  
  // If savings is positive, it's green. If negative, we just don't show a savings block in the bar,
  // but instead the rent+expenses will take up 100% of the bar.
  const savingsPct = savings > 0 ? (savings / maxBarValue) * 100 : 0;

  return (
    <div className="glass-card" style={{ padding: '2rem', marginTop: '4rem' }}>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Cost-of-Living Calculator</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.95rem' }}>
        Estimate your monthly disposable income in <strong>{locality.name}</strong>.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '3rem', alignItems: 'start' }}>
        
        {/* Left Column: Inputs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Salary Input */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Monthly Salary (₹)</label>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                ₹{salary.toLocaleString('en-IN')}
              </span>
            </div>
            <input
              type="range"
              min="20000"
              max="300000"
              step="5000"
              value={salary}
              onChange={(e) => setSalary(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
          </div>

          {/* Lifestyle Expenses Input */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Lifestyle & Groceries (₹)</label>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                ₹{lifestyleExpenses.toLocaleString('en-IN')}
              </span>
            </div>
            <input
              type="range"
              min="5000"
              max="100000"
              step="1000"
              value={lifestyleExpenses}
              onChange={(e) => setLifestyleExpenses(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent)' }}
            />
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Default estimated using locality's Cost of Living Index ({colIndex}/10)
            </div>
          </div>
          
        </div>

        {/* Right Column: Visual Summary */}
        <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
            Monthly Breakdown
          </h3>
          
          {/* Legend & Exact Values */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--danger)' }}></div>
                <span style={{ fontSize: '0.95rem' }}>Average Rent (1BHK)</span>
              </div>
              <span style={{ fontWeight: 600 }}>₹{rent.toLocaleString('en-IN')}</span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--warning)' }}></div>
                <span style={{ fontSize: '0.95rem' }}>Lifestyle</span>
              </div>
              <span style={{ fontWeight: 600 }}>₹{lifestyleExpenses.toLocaleString('en-IN')}</span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px dashed var(--border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: savings >= 0 ? 'var(--success)' : 'var(--danger)' }}></div>
                <span style={{ fontSize: '0.95rem', fontWeight: 700 }}>Disposable Savings</span>
              </div>
              <span style={{ fontWeight: 800, fontSize: '1.25rem', color: savings >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                {savings >= 0 ? '+' : '-'}₹{Math.abs(savings).toLocaleString('en-IN')}
              </span>
            </div>
          </div>

          {/* Segmented Bar Chart */}
          <div style={{ width: '100%', height: '24px', display: 'flex', borderRadius: '12px', overflow: 'hidden', background: 'var(--bg-input)' }}>
            <div style={{ width: `${rentPct}%`, background: 'var(--danger)', transition: 'width 0.3s ease' }} title={`Rent: ${Math.round(rentPct)}%`}></div>
            <div style={{ width: `${expensesPct}%`, background: 'var(--warning)', transition: 'width 0.3s ease' }} title={`Expenses: ${Math.round(expensesPct)}%`}></div>
            {savings > 0 && (
              <div style={{ width: `${savingsPct}%`, background: 'var(--success)', transition: 'width 0.3s ease' }} title={`Savings: ${Math.round(savingsPct)}%`}></div>
            )}
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span>₹0</span>
            <span>Total: ₹{maxBarValue.toLocaleString('en-IN')}</span>
          </div>

        </div>

      </div>
    </div>
  );
}
