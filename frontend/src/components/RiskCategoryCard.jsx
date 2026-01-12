/**
 * RiskCategoryCard Component
 * Expandable card for individual risk category with details
 */
import { useState } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, AlertCircle, CheckCircle, Info } from 'lucide-react';

// Risk level styling
const LEVEL_STYLES = {
  Low: { 
    bg: 'bg-emerald-50', 
    text: 'text-emerald-700', 
    border: 'border-emerald-200',
    badge: 'bg-emerald-100 text-emerald-800',
    icon: CheckCircle,
  },
  Medium: { 
    bg: 'bg-amber-50', 
    text: 'text-amber-700', 
    border: 'border-amber-200',
    badge: 'bg-amber-100 text-amber-800',
    icon: Info,
  },
  High: { 
    bg: 'bg-red-50', 
    text: 'text-red-700', 
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-800',
    icon: AlertCircle,
  },
  Critical: { 
    bg: 'bg-red-100', 
    text: 'text-red-800', 
    border: 'border-red-300',
    badge: 'bg-red-200 text-red-900',
    icon: AlertCircle,
  },
};

// German level names
const LEVEL_NAMES_DE = {
  Low: 'Niedrig',
  Medium: 'Mittel',
  High: 'Hoch',
  Critical: 'Kritisch',
};

export default function RiskCategoryCard({ category, defaultExpanded = false }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!category) return null;

  const { name_de, icon, score, level, factors, recommendations, data } = category;
  const styles = LEVEL_STYLES[level] || LEVEL_STYLES.Low;
  const StatusIcon = styles.icon;

  // Score color based on value
  const getScoreColor = () => {
    if (score >= 60) return 'text-red-600';
    if (score >= 35) return 'text-amber-600';
    return 'text-emerald-600';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-xl border ${styles.border} overflow-hidden transition-all duration-200 hover:shadow-md`}
    >
      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center space-x-3">
          {/* Icon */}
          <span className="text-2xl">{icon}</span>
          
          {/* Name & Level */}
          <div>
            <h4 className="text-sm font-bold text-slate-800">{name_de}</h4>
            <span className={`inline-flex items-center space-x-1 text-xs font-medium ${styles.text}`}>
              <StatusIcon className="w-3 h-3" />
              <span>{LEVEL_NAMES_DE[level]} Risiko</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Score Badge */}
          <div className={`px-3 py-1.5 rounded-lg ${styles.badge} font-bold text-sm`}>
            {score}/100
          </div>
          
          {/* Expand Icon */}
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-5 h-5 text-slate-400" />
          </motion.div>
        </div>
      </button>

      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className={`px-4 pb-4 pt-2 ${styles.bg} border-t ${styles.border}`}>
              {/* Risk Factors */}
              {factors && factors.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Einflussfaktoren
                  </h5>
                  <ul className="space-y-1.5">
                    {factors.map((factor, index) => (
                      <li 
                        key={index}
                        className="flex items-start space-x-2 text-sm text-slate-700"
                      >
                        <span className="text-slate-400 mt-0.5">•</span>
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {recommendations && recommendations.length > 0 && (
                <div className="mb-4">
                  <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Empfehlungen
                  </h5>
                  <ul className="space-y-1.5">
                    {recommendations.map((rec, index) => (
                      <li 
                        key={index}
                        className="flex items-start space-x-2 text-sm text-slate-600"
                      >
                        <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Data Points */}
              {data && Object.keys(data).length > 0 && (
                <div className="bg-white/50 rounded-lg p-3">
                  <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Messwerte
                  </h5>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(data).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <span className="text-slate-500">{formatDataKey(key)}: </span>
                        <span className="font-semibold text-slate-800">{formatDataValue(key, value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// Helper functions for formatting
function formatDataKey(key) {
  const keyMap = {
    elevation_m: 'Höhe',
    relative_height_m: 'Rel. Höhe',
    max_gust_kmh: 'Max. Böe',
    storm_days_per_year: 'Sturmtage/Jahr',
    fire_weather_index: 'Feuer-Index',
    drought_days: 'Trocken-Tage/Jahr',
    heat_days: 'Hitzetage/Jahr',
    frost_days: 'Frosttage/Jahr',
    heavy_precip_days: 'Starkregen-Tage',
    zone: 'Zone',
    zone_name: 'Erdbebenzone',
  };
  return keyMap[key] || key;
}

function formatDataValue(key, value) {
  if (key.includes('_m') && typeof value === 'number') {
    return `${value.toFixed(1)} m`;
  }
  if (key.includes('kmh') && typeof value === 'number') {
    return `${value.toFixed(0)} km/h`;
  }
  if (key.includes('days') && typeof value === 'number') {
    return `${value.toFixed(0)} Tage`;
  }
  if (typeof value === 'number') {
    return value.toFixed(1);
  }
  return String(value);
}

RiskCategoryCard.propTypes = {
  category: PropTypes.shape({
    name: PropTypes.string,
    name_de: PropTypes.string,
    icon: PropTypes.string,
    score: PropTypes.number,
    level: PropTypes.string,
    factors: PropTypes.arrayOf(PropTypes.string),
    recommendations: PropTypes.arrayOf(PropTypes.string),
    data: PropTypes.object,
  }),
  defaultExpanded: PropTypes.bool,
};
