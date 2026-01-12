/**
 * InsuranceCard Component
 * Displays insurance recommendations and cost estimates
 */
import { motion } from 'framer-motion';
import { Shield, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import PropTypes from 'prop-types';

export default function InsuranceCard({ data }) {
  if (!data || !data.recommendations) return null;

  const { recommendations, total_annual_cost_estimate_eur, comparison_to_average } = data;

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Erforderlich':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'Empfohlen':
        return 'bg-amber-100 text-amber-700 border-amber-300';
      case 'Optional':
        return 'bg-slate-100 text-slate-700 border-slate-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'Erforderlich':
        return <AlertCircle className="w-4 h-4" />;
      case 'Empfohlen':
        return <Shield className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
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
          <div className="p-2 bg-primary-100 rounded-xl">
            <Shield className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Versicherungsempfehlungen</h3>
            <p className="text-sm text-slate-500">Maßgeschneiderter Schutz für Ihr Objekt</p>
          </div>
        </div>
      </div>

      {/* Cost Summary */}
      <div className="bg-gradient-to-br from-primary-50 to-amber-50 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-600 font-medium mb-1">Geschätzte Jahreskosten</p>
            <p className="text-2xl font-bold text-slate-900">
              {total_annual_cost_estimate_eur[0]}-{total_annual_cost_estimate_eur[1]}€
            </p>
            <p className="text-xs text-slate-600 mt-1">{comparison_to_average}</p>
          </div>
          <TrendingUp className="w-8 h-8 text-primary-600" />
        </div>
      </div>

      {/* Recommendations */}
      <div className="space-y-4">
        {recommendations.map((rec, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow"
          >
            {/* Recommendation Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h4 className="font-bold text-slate-900">{rec.type}</h4>
                  <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border flex items-center space-x-1 ${getPriorityColor(rec.priority)}`}>
                    {getPriorityIcon(rec.priority)}
                    <span>{rec.priority}</span>
                  </span>
                </div>
                <p className="text-sm text-slate-600 mb-2">{rec.reasoning}</p>
              </div>
            </div>

            {/* Cost */}
            <div className="bg-slate-50 rounded-lg p-3 mb-3">
              <p className="text-xs text-slate-500 mb-1">Geschätzte jährliche Kosten</p>
              <p className="text-lg font-bold text-slate-900">
                {rec.estimated_annual_cost_eur[0]}-{rec.estimated_annual_cost_eur[1]}€
                <span className="text-sm font-normal text-slate-500 ml-2">pro Jahr</span>
              </p>
            </div>

            {/* Coverage Details */}
            <div className="mb-3">
              <p className="text-xs font-semibold text-slate-700 mb-2">Abgedeckte Schäden:</p>
              <ul className="space-y-1">
                {rec.coverage_details.map((detail, idx) => (
                  <li key={idx} className="text-xs text-slate-600 flex items-start">
                    <CheckCircle className="w-3 h-3 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Provider Tips */}
            {rec.provider_tips && rec.provider_tips.length > 0 && (
              <details className="text-xs">
                <summary className="cursor-pointer text-primary-600 font-semibold hover:text-primary-700">
                  💡 Profi-Tipps anzeigen
                </summary>
                <ul className="mt-2 space-y-1 pl-4">
                  {rec.provider_tips.map((tip, idx) => (
                    <li key={idx} className="text-slate-600">• {tip}</li>
                  ))}
                </ul>
              </details>
            )}
          </motion.div>
        ))}
      </div>

      {/* Footer Note */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-900">
          <strong>Hinweis:</strong> Diese Empfehlungen basieren auf Ihrem Risikoprofil und deutschen Marktdurchschnitten.
          Für eine individuelle Beratung kontaktieren Sie einen Versicherungsmakler.
        </p>
      </div>
    </motion.div>
  );
}

InsuranceCard.propTypes = {
  data: PropTypes.shape({
    recommendations: PropTypes.arrayOf(PropTypes.shape({
      type: PropTypes.string,
      priority: PropTypes.string,
      estimated_annual_cost_eur: PropTypes.arrayOf(PropTypes.number),
      coverage_details: PropTypes.arrayOf(PropTypes.string),
      reasoning: PropTypes.string,
      provider_tips: PropTypes.arrayOf(PropTypes.string),
    })),
    total_annual_cost_estimate_eur: PropTypes.arrayOf(PropTypes.number),
    comparison_to_average: PropTypes.string,
  }),
};
