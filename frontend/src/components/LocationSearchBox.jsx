import { useState, useEffect, useRef } from 'react';

export default function LocationSearchBox({ onLocationSelect, placeholder = "Type a location..." }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  // Close dropdown if clicked outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  // Debounced API call to Nominatim
  useEffect(() => {
    if (!query || query.length < 3) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    const fetchLocations = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5`
        );
        const data = await response.json();
        setResults(data);
        setIsOpen(true);
      } catch (error) {
        console.error("Geocoding error:", error);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(() => {
      fetchLocations();
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelect = (result) => {
    setQuery(result.display_name); // Set input text to selected name
    setIsOpen(false);
    onLocationSelect({
      lat: parseFloat(result.lat),
      lng: parseFloat(result.lon),
      name: result.display_name
    });
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    onLocationSelect({ lat: null, lng: null, name: '' });
  };

  return (
    <div ref={wrapperRef} style={{ position: 'relative', width: '100%' }}>
      <div style={{ position: 'relative' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            // If user clears the input, clear the selection
            if (e.target.value === '') {
              onLocationSelect({ lat: null, lng: null, name: '' });
            }
          }}
          onFocus={() => {
            if (results.length > 0) setIsOpen(true);
          }}
          placeholder={placeholder}
          style={{
            width: '100%',
            padding: '0.75rem',
            paddingRight: '2.5rem',
            borderRadius: 'var(--radius)',
            background: 'var(--bg-input)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            outline: 'none'
          }}
        />
        {query && (
          <button 
            onClick={handleClear}
            style={{
              position: 'absolute',
              right: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              fontSize: '1.2rem'
            }}
          >
            ×
          </button>
        )}
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div style={{ position: 'absolute', top: '12px', right: query ? '35px' : '10px', color: 'var(--accent)' }}>
          <span className="spinner" style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
        </div>
      )}

      {/* Dropdown Results */}
      {isOpen && results.length > 0 && (
        <ul style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          marginTop: '0.25rem',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
          listStyle: 'none',
          padding: 0,
          margin: 0,
          maxHeight: '200px',
          overflowY: 'auto',
          zIndex: 100,
          boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
        }}>
          {results.map((result) => (
            <li 
              key={result.place_id}
              onClick={() => handleSelect(result)}
              style={{
                padding: '0.75rem 1rem',
                borderBottom: '1px solid var(--border)',
                cursor: 'pointer',
                fontSize: '0.85rem',
                color: 'var(--text-primary)',
                transition: 'background 0.2s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-input)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              {result.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
