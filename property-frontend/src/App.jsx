import { useState, useEffect } from 'react';
import './App.css'; // Ensure this matches your CSS file name exactly

function App() {
  // State for the search bar and autocomplete
  const [address, setAddress] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // State for handling backend data and UI feedback
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-complete feature: Fetches street addresses as the user types
  useEffect(() => {
    // Only search if they have typed at least 3 characters
    if (address.length < 3) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/search-address?query=${encodeURIComponent(address)}`);
        if (response.ok) {
          const data = await response.json();
          setSuggestions(data);
        }
      } catch (err) {
        console.error("Failed to fetch suggestions", err);
      }
    };

    // Small delay (debounce) so we don't spam the backend on every single keystroke
    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [address]);

  // Main search function: Calls the Haversine/bounding box cascade algorithm
  const handleSearch = async (searchTarget) => {
    const targetAddress = searchTarget || address;
    if (!targetAddress) return;

    // Reset UI states before starting the search
    setLoading(true);
    setError(null);
    setShowSuggestions(false);
    setAddress(targetAddress); // Lock the input to what they selected

    try {
      const response = await fetch(`http://127.0.0.1:8000/similar-properties?address=${encodeURIComponent(targetAddress)}`);
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setResults(null);
      } else {
        setResults(data);
      }
    } catch (err) {
      setError("Failed to connect to the backend. Make sure FastAPI is running on port 8000!");
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header Section */}
      <div className="header-section">
        <h1>Property Assessment Explorer</h1>
        <p>Find comparable real estate values using spatial Haversine algorithms and bounding box optimization.</p>
      </div>

      {/* Search Controls */}
      <div className="search-container">
        <div className="search-box">
          <div className="search-input-wrapper">
            <input
              type="text"
              className="search-input"
              placeholder="Type a real Fort Bend address..."
              value={address}
              onChange={(e) => {
                setAddress(e.target.value);
                setShowSuggestions(true);
              }}
              onFocus={() => setShowSuggestions(true)}
            />

            {/* Dropdown Menu for Autocomplete */}
            {showSuggestions && suggestions.length > 0 && (
              <ul className="suggestions-list">
                {suggestions.map((suggestion, index) => (
                  <li
                    key={index}
                    // When clicked, immediately trigger the main search
                    onClick={() => handleSearch(suggestion)}
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <button className="search-btn" onClick={() => handleSearch()}>
            Search Similar
          </button>
        </div>
      </div>

      {/* Loading & Error Feedback */}
      {loading && <div className="loading-spinner">Running spatial query cascade...</div>}
      {error && <div className="no-results" style={{color: '#b91c1c'}}>{error}</div>}

      {/* Main Results Display */}
      {results && !loading && !error && (
        <div className="results-section">

          {/* §41.43(b)(3) Statutory Dashboard */}
          <div className="statutory-dashboard">
            <div className="stat-box">
              <h4>Target Property Value</h4>
              <div className="stat-val">{results.target.val}</div>
              <div style={{ color: '#64748b', fontSize: '0.85rem' }}>{results.target.ppsf_display}</div>
            </div>
            <div className="stat-box">
              <h4>Comps Found</h4>
              <div className="stat-val">{results.metrics.comps_found}</div>
              <div className="tier-val">Tier {results.metrics.tier_used} Match</div>
            </div>
            <div className="stat-box">
              <h4>Median Comp Price</h4>
              <div className="stat-val">{results.metrics.median_ppsf}</div>
              <div style={{ color: '#64748b', fontSize: '0.85rem' }}>Used for tax protests</div>
            </div>
          </div>

          {/* Subheader showing which cascade tier successfully found results */}
          <h2>Comparable Properties (Filtered by: {results.metrics.tier_desc})</h2>

          {/* Property Cards List */}
          <div className="results-list">
            {results.comps.map((comp, idx) => (
              <div className="card" key={idx}>
                <div className="card-info">
                  <h3>{comp.address}</h3>
                  <div className="card-subtext">
                    {comp.sqft} sqft • Built {comp.age_diff} yrs from target
                  </div>

                  {/* Visual indicators for how close of a match this property is */}
                  <div className="match-badges">
                    <span className={`quality-badge ${comp.badge}`}>
                      {comp.sqft_diff_pct}% size diff
                    </span>
                    {comp.is_capped && (
                      <span className="warning-badge">Exempt/Capped</span>
                    )}
                  </div>
                </div>

                <div className="card-price-block">
                  <div className="card-price">{comp.ppsf_display}</div>
                  <div className="card-total">Total: {comp.val}</div>
                </div>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  );
}

export default App;