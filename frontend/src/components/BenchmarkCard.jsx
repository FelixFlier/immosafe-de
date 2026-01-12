/**
 * BenchmarkCard Component
 * Displays regional comparisons and benchmarking data
 */
import { motion } from 'framer-motion';
import { BarChart3, MapPin, TrendingDown, TrendingUp, Award } from 'lucide-react';
import PropTypes from 'prop-types';

export default function BenchmarkCard({ data }) {
  if (!data) return null;

  const { city_name, state_name, comparisons, overall_ranking, summary, nearby_high_risk_areas } = data;

  const getRankingColor = (ranking) => {
    switch (ranking) {
      case 'Sehr gut':
        return 'text-green-600 bg-green-100 border-green-300';
      case 'Gut':
        return 'text-emerald-600 bg-emerald-100 border-emerald-300';
      case 'Durchschnittlich':
        return 'text-slate-600 bg-slate-100 border-slate-300';
      case 'Erhöht':
        return 'text-amber-600 bg-amber-100 border-amber-300';
      case 'Hoch':
        return 'text-red-600 bg-red-100 border-red-300';
      default:
        return 'text-slate-600 bg-slate-100 border-slate-300';
    }
  };

  const getPercentileColor = (percentile) => {
    if (percentile >= 70) return 'bg-green-500';
    if (percentile >= 50) return 'bg-emerald-500';
    if (percentile >= 30) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-100 rounded-xl">
            <BarChart3 className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Regionaler Vergleich</h3>
            <p className="text-sm text-slate-500 flex items-center">
              <MapPin className="w-3 h-3 mr-1" />
              {city_name !== 'Unbekannt' ? city_name + ', ' : ''}{state_name}
            </p>
          </div>
        </div>
        <div className={`px-3 py-1.5 rounded-xl border font-bold text-sm ${getRankingColor(overall_ranking)}`}>
          {overall_ranking}
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-4 mb-6">
        <p className="text-sm text-slate-700 leading-relaxed">{summary}</p>
      </div>

      {/* Comparisons */}
      <div className="space-y-4 mb-6">
        {comparisons.map((comp, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="border border-slate-200 rounded-xl p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex-1">
                <p className="font-semibold text-slate-900">{comp.metric}</p>
                <p className="text-xs text-slate-500 mt-1">{comp.comparison_text}</p>
              </div>
              <div className="text-right ml-4">
                {comp.location_value < comp.region_average ? (
                  <TrendingDown className="w-5 h-5 text-green-500 inline mr-1" />
                ) : (
                  <TrendingUp className="w-5 h-5 text-amber-500 inline mr-1" />
                )}
                <span className="text-lg font-bold text-slate-900">{comp.location_value}</span>
                <span className="text-xs text-slate-500 ml-1">/ {comp.region_average}</span>
              </div>
            </div>

            {/* Percentile Bar */}
            <div className="relative">
              <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getPercentileColor(comp.percentile)} transition-all duration-500`}
                  style={{ width: `${comp.percentile}%` }}
                />
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-slate-400">Schlechter</span>
                <span className="text-xs font-semibold text-slate-600">{comp.percentile}. Perzentil</span>
                <span className="text-xs text-slate-400">Besser</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Nearby High-Risk Areas */}
      {nearby_high_risk_areas && nearby_high_risk_areas.length > 0 && (
        <div className="border-t border-slate-200 pt-4">
          <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center">
            <Award className="w-4 h-4 mr-1 text-amber-500" />
            Bekannte Risikogebiete in der Region:
          </p>
          <div className="flex flex-wrap gap-2">
            {nearby_high_risk_areas.map((area, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-amber-50 text-amber-700 text-xs font-medium rounded-full border border-amber-200"
              >
                {area}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Info Note */}
      <div className="mt-6 p-3 bg-slate-50 border border-slate-200 rounded-lg">
        <p className="text-xs text-slate-600">
          <strong>Kontext:</strong> Diese Vergleiche basieren auf historischen Wetterdaten und regionalen Durchschnittswerten.
          Ihr Standort wird mit ähnlichen Lagen in {state_name} verglichen.
        </p>
      </div>
    </motion.div>
  );
}

BenchmarkCard.propTypes = {
  data: PropTypes.shape({
    city_name: PropTypes.string,
    state_name: PropTypes.string,
    comparisons: PropTypes.arrayOf(PropTypes.shape({
      metric: PropTypes.string,
      location_value: PropTypes.number,
      region_average: PropTypes.number,
      percentile: PropTypes.number,
      comparison_text: PropTypes.string,
    })),
    overall_ranking: PropTypes.string,
    summary: PropTypes.string,
    nearby_high_risk_areas: PropTypes.arrayOf(PropTypes.string),
  }),
};
