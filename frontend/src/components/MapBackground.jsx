/**
 * MapBackground Component
 * Full-screen Google Map with marker support, map type toggle, and risk circle
 */
import { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { Map, Marker, useMap } from '@vis.gl/react-google-maps';
import { Layers } from 'lucide-react';

/**
 * Custom Circle component using native Google Maps API
 * since @vis.gl/react-google-maps doesn't export Circle directly
 */
function Circle({ center, radius, fillColor, fillOpacity, strokeColor, strokeOpacity, strokeWeight }) {
  const map = useMap();
  const circleRef = useRef(null);

  useEffect(() => {
    if (!map) return;

    // Create circle if it doesn't exist
    if (!circleRef.current) {
      circleRef.current = new google.maps.Circle({
        map,
        center,
        radius,
        fillColor,
        fillOpacity,
        strokeColor,
        strokeOpacity,
        strokeWeight,
      });
    } else {
      // Update existing circle
      circleRef.current.setCenter(center);
      circleRef.current.setRadius(radius);
      circleRef.current.setOptions({
        fillColor,
        fillOpacity,
        strokeColor,
        strokeOpacity,
        strokeWeight,
      });
    }

    return () => {
      if (circleRef.current) {
        circleRef.current.setMap(null);
        circleRef.current = null;
      }
    };
  }, [map, center, radius, fillColor, fillOpacity, strokeColor, strokeOpacity, strokeWeight]);

  return null;
}

Circle.propTypes = {
  center: PropTypes.shape({
    lat: PropTypes.number.isRequired,
    lng: PropTypes.number.isRequired,
  }).isRequired,
  radius: PropTypes.number.isRequired,
  fillColor: PropTypes.string,
  fillOpacity: PropTypes.number,
  strokeColor: PropTypes.string,
  strokeOpacity: PropTypes.number,
  strokeWeight: PropTypes.number,
};

/**
 * Get circle fill color based on risk level
 */
function getRiskColor(level) {
  switch (level?.toLowerCase()) {
    case 'low':
      return '#22c55e'; // Green
    case 'medium':
      return '#f59e0b'; // Amber/Orange
    case 'high':
      return '#ef4444'; // Red
    default:
      return '#6b7280'; // Gray
  }
}

export default function MapBackground({ coordinates, riskLevel, showRiskCircle }) {
  const [mapType, setMapType] = useState('roadmap');
  const [circleRadius, setCircleRadius] = useState(150);
  
  // Pulse animation effect for the circle
  useEffect(() => {
    if (!showRiskCircle) return;
    
    let growing = true;
    const minRadius = 140;
    const maxRadius = 160;
    const step = 2;
    
    const interval = setInterval(() => {
      setCircleRadius(prev => {
        if (growing) {
          if (prev >= maxRadius) {
            growing = false;
            return prev - step;
          }
          return prev + step;
        } else {
          if (prev <= minRadius) {
            growing = true;
            return prev + step;
          }
          return prev - step;
        }
      });
    }, 100);
    
    return () => clearInterval(interval);
  }, [showRiskCircle]);

  const toggleMapType = () => {
    setMapType(prev => (prev === 'roadmap' ? 'hybrid' : 'roadmap'));
  };

  const isLocationSelected = coordinates.lat !== 51.16;
  const riskColor = getRiskColor(riskLevel);

  return (
    <>
      <Map
        style={{ width: '100%', height: '100%' }}
        defaultCenter={coordinates}
        center={coordinates}
        defaultZoom={7}
        zoom={isLocationSelected ? 16 : 7}
        gestureHandling="greedy"
        disableDefaultUI={false}
        mapTypeId={mapType}
        mapId="immosafe-map"
      >

        {/* Location Marker */}
        {isLocationSelected && (
          <Marker position={coordinates} />
        )}
        
        {/* Risk Visualization Circle */}
        {showRiskCircle && isLocationSelected && (
          <Circle
            center={coordinates}
            radius={circleRadius}
            strokeColor="transparent"
            strokeOpacity={0}
            strokeWeight={0}
            fillColor={riskColor}
            fillOpacity={0.35}
          />
        )}
      </Map>
      
      {/* Map Type Toggle Button */}
      <button
        onClick={toggleMapType}
        className="absolute top-4 right-4 z-20 bg-white hover:bg-gray-50 shadow-lg rounded-lg p-3 transition-all duration-200 group md:right-[340px]"
        title={`Switch to ${mapType === 'roadmap' ? 'Satellite' : 'Map'} view`}
      >
        <Layers className="w-5 h-5 text-gray-600 group-hover:text-primary-600 transition-colors" />
        <span className="sr-only">Toggle Map Type</span>
      </button>
    </>
  );
}

MapBackground.propTypes = {
  coordinates: PropTypes.shape({
    lat: PropTypes.number.isRequired,
    lng: PropTypes.number.isRequired,
  }).isRequired,
  riskLevel: PropTypes.string,
  showRiskCircle: PropTypes.bool,
};

MapBackground.defaultProps = {
  riskLevel: null,
  showRiskCircle: false,
};
