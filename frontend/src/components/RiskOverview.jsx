/**
 * RiskOverview Component
 * Displays overall risk score with radar chart and primary risks summary
 */
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';

// Risk level colors
const RISK_COLORS = {
  Low: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', dot: 'bg-emerald-500' },
  Medium: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500' },
  High: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' },
  Critical: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300', dot: 'bg-red-600' },
};

// Risk category icons (emoji)
const RISK_ICONS = {
  flood_risk: '🌊',
  storm_risk: '🌪️',
  fire_risk: '🔥',
  temperature_risk: '🌡️',
  hail_risk: '⚡',
  earthquake_risk: '🏔️',
};

export default function RiskOverview({ data }) {
  if (!data) return null;

  const { total_risk_score, total_risk_level, primary_risks } = data;
  const levelStyles = RISK_COLORS[total_risk_level] || RISK_COLORS.Low;

  // Collect all risk scores for the radar visualization
  const riskCategories = [
    { key: 'flood_risk', label: 'Hochwasser', score: data.flood_risk?.score || 0 },
    { key: 'storm_risk', label: 'Sturm', score: data.storm_risk?.score || 0 },
    { key: 'fire_risk', label: 'Waldbrand', score: data.fire_risk?.score || 0 },
    { key: 'temperature_risk', label: 'Temperatur', score: data.temperature_risk?.score || 0 },
    { key: 'hail_risk', label: 'Hagel', score: data.hail_risk?.score || 0 },
    { key: 'earthquake_risk', label: 'Erdbeben', score: data.earthquake_risk?.score || 0 },
  ];

  // Get score color based on value
  const getScoreColor = (score) => {
    if (score >= 60) return 'text-red-600';
    if (score >= 35) return 'text-amber-600';
    return 'text-emerald-600';
  };

  const getBarColor = (score) => {
    if (score >= 60) return 'bg-red-500';
    if (score >= 35) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Main Risk Score Card */}
      <div className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-2xl p-6 border border-slate-200/60">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Gesamtrisiko-Bewertung
          </h2>
          <span className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold ${levelStyles.bg} ${levelStyles.text} border ${levelStyles.border}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${levelStyles.dot} animate-pulse`}></span>
            <span>{total_risk_level === 'Low' ? 'Niedriges' : total_risk_level === 'Medium' ? 'Mittleres' : 'Hohes'} Risiko</span>
          </span>
        </div>

        {/* Large Score Display */}
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            {/* Score Circle */}
            <div className={`w-32 h-32 rounded-full border-8 ${
              total_risk_score >= 60 ? 'border-red-200' : 
              total_risk_score >= 35 ? 'border-amber-200' : 
              'border-emerald-200'
            } flex items-center justify-center bg-white shadow-lg`}>
              <div className="text-center">
                <span className={`text-4xl font-bold ${getScoreColor(total_risk_score)}`}>
                  {total_risk_score}
                </span>
                <span className="text-sm text-slate-400 block">/100</span>
              </div>
            </div>
            
            {/* Icon */}
            <div className={`absolute -bottom-2 -right-2 w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
              total_risk_score >= 60 ? 'bg-red-500' : 
              total_risk_score >= 35 ? 'bg-amber-500' : 
              'bg-emerald-500'
            }`}>
              {total_risk_score >= 60 ? (
                <AlertTriangle className="w-5 h-5 text-white" />
              ) : total_risk_score >= 35 ? (
                <Info className="w-5 h-5 text-white" />
              ) : (
                <CheckCircle className="w-5 h-5 text-white" />
              )}
            </div>
          </div>
        </div>

        {/* Primary Risks */}
        {primary_risks && primary_risks.length > 0 && (
          <div className="text-center">
            <p className="text-xs text-slate-500 mb-2">Hauptrisiken:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {primary_risks.map((risk, index) => (
                <span 
                  key={index}
                  className="px-3 py-1 bg-white rounded-lg text-sm font-medium text-slate-700 border border-slate-200"
                >
                  {risk}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Risk Breakdown Bars */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">
          Risiko nach Kategorie
        </h3>
        <div className="space-y-3">
          {riskCategories.map((category) => (
            <div key={category.key} className="flex items-center space-x-3">
              {/* Icon */}
              <span className="text-lg w-6 text-center">{RISK_ICONS[category.key]}</span>
              
              {/* Label */}
              <span className="text-sm font-medium text-slate-600 w-24 truncate">
                {category.label}
              </span>
              
              {/* Bar */}
              <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${category.score}%` }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                  className={`h-full rounded-full ${getBarColor(category.score)}`}
                />
              </div>
              
              {/* Score */}
              <span className={`text-sm font-bold w-8 text-right ${getScoreColor(category.score)}`}>
                {category.score}
              </span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

RiskOverview.propTypes = {
  data: PropTypes.shape({
    total_risk_score: PropTypes.number,
    total_risk_level: PropTypes.string,
    primary_risks: PropTypes.arrayOf(PropTypes.string),
    flood_risk: PropTypes.object,
    storm_risk: PropTypes.object,
    fire_risk: PropTypes.object,
    temperature_risk: PropTypes.object,
    hail_risk: PropTypes.object,
    earthquake_risk: PropTypes.object,
  }),
};
