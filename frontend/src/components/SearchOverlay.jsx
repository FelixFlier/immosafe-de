/**
 * SearchOverlay Component
 * Floating search card with Google Places Autocomplete
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Search, MapPin, X } from 'lucide-react';
import { useMapsLibrary } from '@vis.gl/react-google-maps';

export default function SearchOverlay({ onSearch, loading }) {
  const [address, setAddress] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const autocompleteServiceRef = useRef(null);

  // Load the Places library using useMapsLibrary
  const placesLibrary = useMapsLibrary('places');

  // Initialize AutocompleteService when places library is loaded
  useEffect(() => {
    if (placesLibrary) {
      autocompleteServiceRef.current = new placesLibrary.AutocompleteService();
    }
  }, [placesLibrary]);

  // Fetch predictions when address changes
  const fetchPredictions = useCallback((input) => {
    if (!autocompleteServiceRef.current || input.length <= 2) {
      setPredictions([]);
      setShowDropdown(false);
      return;
    }

    autocompleteServiceRef.current.getPlacePredictions(
      {
        input,
        componentRestrictions: { country: 'de' },
        types: ['address'],
      },
      (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results) {
          setPredictions(results);
          setShowDropdown(true);
          setHighlightedIndex(-1);
        } else {
          setPredictions([]);
          setShowDropdown(false);
        }
      }
    );
  }, []);

  // Debounce the fetch predictions call
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchPredictions(address);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [address, fetchPredictions]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    setAddress(e.target.value);
  };

  const handlePredictionClick = (prediction) => {
    const fullAddress = prediction.description;
    setAddress(fullAddress);
    setPredictions([]);
    setShowDropdown(false);
    // Trigger search immediately
    onSearch(fullAddress);
  };

  const handleClear = () => {
    setAddress('');
    setPredictions([]);
    setShowDropdown(false);
    inputRef.current?.focus();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (address.trim()) {
      setShowDropdown(false);
      onSearch(address.trim());
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!showDropdown || predictions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < predictions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < predictions.length) {
          handlePredictionClick(predictions[highlightedIndex]);
        } else if (address.trim()) {
          setShowDropdown(false);
          onSearch(address.trim());
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setHighlightedIndex(-1);
        break;
      default:
        break;
    }
  };

  return (
    <div className="absolute top-0 left-0 right-0 md:top-4 md:left-4 md:right-auto z-10 w-full md:w-80 bg-white shadow-xl md:rounded-lg p-4">
      {/* Logo Header */}
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">IS</span>
        </div>
        <h1 className="text-lg font-bold text-gray-900">ImmoSafe DE</h1>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit}>
        <div className="relative mb-3">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={address}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              if (predictions.length > 0) setShowDropdown(true);
            }}
            placeholder="Enter Address..."
            className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all duration-200"
            disabled={loading}
            autoComplete="off"
          />
          {/* Clear Button */}
          {address && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 hover:text-gray-600 transition-colors duration-150"
              aria-label="Clear search"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {/* Predictions Dropdown */}
          {showDropdown && predictions.length > 0 && (
            <div
              ref={dropdownRef}
              className="absolute top-full left-0 right-0 mt-1 bg-white shadow-lg rounded-lg border border-gray-200 max-h-60 overflow-y-auto z-20"
            >
              {predictions.map((prediction, index) => (
                <button
                  key={prediction.place_id}
                  type="button"
                  onClick={() => handlePredictionClick(prediction)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`w-full px-4 py-3 text-left text-sm transition-colors duration-150 flex items-start space-x-3 ${
                    index === highlightedIndex
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  } ${index === 0 ? 'rounded-t-lg' : ''} ${
                    index === predictions.length - 1 ? 'rounded-b-lg' : ''
                  }`}
                >
                  <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0 text-gray-400" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">
                      {prediction.structured_formatting?.main_text || prediction.description}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {prediction.structured_formatting?.secondary_text || ''}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        <button
          type="submit"
          disabled={loading || !address.trim()}
          className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-300 text-white font-medium py-2.5 px-5 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Analyze Risk</span>
            </>
          )}
        </button>
      </form>

      {/* Info Text */}
      <p className="text-xs text-gray-500 mt-3 text-center">
        Enter a German address to analyze flood risk
      </p>
    </div>
  );
}

SearchOverlay.propTypes = {
  onSearch: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};
