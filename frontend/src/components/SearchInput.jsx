/**
 * SearchInput Component
 * Premium "Hero Search" bar with Google Places Autocomplete
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Search, MapPin, X } from 'lucide-react';
import { useMapsLibrary } from '@vis.gl/react-google-maps';

export default function SearchInput({ onSearch, loading }) {
  const [address, setAddress] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [isFocused, setIsFocused] = useState(false);
  
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const autocompleteServiceRef = useRef(null);

  const placesLibrary = useMapsLibrary('places');

  useEffect(() => {
    if (placesLibrary) {
      autocompleteServiceRef.current = new placesLibrary.AutocompleteService();
    }
  }, [placesLibrary]);

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

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchPredictions(address);
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [address, fetchPredictions]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setShowDropdown(false);
        setIsFocused(false);
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
    <div className="space-y-5">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          Property Search
        </h2>
      </div>

      {/* Hero Search Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Premium Search Input with lift effect */}
        <div className={`relative transition-all duration-300 ease-out ${
          isFocused ? '-translate-y-0.5' : ''
        }`}>
          {/* Search Icon - Heavy and prominent */}
          <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-200 ${
            isFocused ? 'text-primary-600 scale-110' : 'text-slate-400'
          }`}>
            <Search className="w-5 h-5 stroke-[2.5]" />
          </div>
          
          <input
            ref={inputRef}
            type="text"
            value={address}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              setIsFocused(true);
              if (predictions.length > 0) setShowDropdown(true);
            }}
            onBlur={() => setIsFocused(false)}
            placeholder="Enter a German address..."
            className={`
              w-full h-14 pl-12 pr-12 
              bg-slate-50 border-2 rounded-2xl
              text-lg text-slate-900 font-medium
              placeholder-slate-400
              outline-none transition-all duration-300 ease-out
              ${isFocused 
                ? 'bg-white border-primary-500 shadow-xl shadow-primary-500/15' 
                : 'border-slate-200 hover:border-slate-300 hover:shadow-md'
              }
            `}
            disabled={loading}
            autoComplete="off"
          />

          {/* Clear Button */}
          {address && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-4 top-1/2 -translate-y-1/2 w-7 h-7 flex items-center justify-center rounded-full bg-slate-200 hover:bg-slate-300 text-slate-500 hover:text-slate-700 transition-all duration-150"
              aria-label="Clear search"
            >
              <X className="w-4 h-4 stroke-[2.5]" />
            </button>
          )}

          {/* Predictions Dropdown */}
          {showDropdown && predictions.length > 0 && (
            <div
              ref={dropdownRef}
              className="absolute top-full left-0 right-0 mt-2 bg-white shadow-soft-lg rounded-2xl border border-slate-200 max-h-72 overflow-y-auto z-50"
            >
              {predictions.map((prediction, index) => (
                <button
                  key={prediction.place_id}
                  type="button"
                  onClick={() => handlePredictionClick(prediction)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`w-full px-5 py-4 text-left transition-all duration-150 flex items-start space-x-4 ${
                    index === highlightedIndex
                      ? 'bg-primary-50'
                      : 'hover:bg-slate-50'
                  } ${index === 0 ? 'rounded-t-2xl' : ''} ${
                    index === predictions.length - 1 ? 'rounded-b-2xl' : 'border-b border-slate-100'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    index === highlightedIndex ? 'bg-primary-100' : 'bg-slate-100'
                  }`}>
                    <MapPin className={`w-4 h-4 ${
                      index === highlightedIndex ? 'text-primary-600' : 'text-slate-500'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0 pt-0.5">
                    <p className={`text-sm font-semibold truncate ${
                      index === highlightedIndex ? 'text-primary-900' : 'text-slate-800'
                    }`}>
                      {prediction.structured_formatting?.main_text || prediction.description}
                    </p>
                    <p className="text-xs text-slate-500 truncate mt-0.5">
                      {prediction.structured_formatting?.secondary_text || ''}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !address.trim()}
          className="
            w-full h-12 
            bg-gradient-to-r from-primary-600 to-primary-700 
            hover:from-primary-700 hover:to-primary-800 
            disabled:from-slate-300 disabled:to-slate-400 
            text-white font-semibold text-sm uppercase tracking-wide
            rounded-xl transition-all duration-200 
            flex items-center justify-center space-x-2.5 
            shadow-lg shadow-primary-600/25 
            disabled:shadow-none
            hover:shadow-xl hover:shadow-primary-600/30
            active:scale-[0.98]
          "
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4 stroke-[2.5]" />
              <span>Analyze Risk</span>
            </>
          )}
        </button>
      </form>

      {/* Helper Text */}
      <p className="text-xs text-slate-400 text-center">
        Enter any German property address for instant risk analysis
      </p>
    </div>
  );
}

SearchInput.propTypes = {
  onSearch: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};
