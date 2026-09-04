/**
 * SearchBar — Simple search input with icon.
 */
export default function SearchBar({ value, onChange, placeholder }) {
  return (
    <div className="search-bar-wrapper">
      <div className="search-bar-container">
        <span className="search-icon"></span>
        <input
          type="text"
          className="search-bar"
          placeholder={placeholder || 'Search cities...'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          id="city-search"
        />
      </div>
    </div>
  );
}
