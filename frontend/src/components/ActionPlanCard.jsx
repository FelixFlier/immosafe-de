/**
 * ActionPlanCard Component
 * Displays actionable recommendations with priorities and costs
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Wrench, Clock, Euro, CheckCircle, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import PropTypes from 'prop-types';

export default function ActionPlanCard({ data }) {
  const [expandedAction, setExpandedAction] = useState(null);

  if (!data) return null;

  const {
    immediate_actions,
    short_term_actions,
    medium_term_actions,
    long_term_actions,
    total_estimated_cost_eur,
    estimated_risk_reduction_percent,
    summary
  } = data;

  const allActions = [
    ...immediate_actions.map(a => ({ ...a, group: 'Sofort' })),
    ...short_term_actions.map(a => ({ ...a, group: 'Kurzfristig' })),
    ...medium_term_actions.map(a => ({ ...a, group: 'Mittelfristig' })),
    ...long_term_actions.map(a => ({ ...a, group: 'Langfristig' })),
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Sofort':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'Kurzfristig':
        return 'bg-amber-100 text-amber-700 border-amber-300';
      case 'Mittelfristig':
        return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'Langfristig':
        return 'bg-slate-100 text-slate-700 border-slate-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Baulich':
        return '🏗️';
      case 'Versicherung':
        return '🛡️';
      case 'Wartung':
        return '🔧';
      case 'Notfallvorsorge':
        return '🚨';
      default:
        return '📋';
    }
  };

  const getUrgencyStars = (urgency) => {
    return '⭐'.repeat(Math.min(urgency, 10));
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
          <div className="p-2 bg-green-100 rounded-xl">
            <Wrench className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Maßnahmenplan</h3>
            <p className="text-sm text-slate-500">{allActions.length} konkrete Handlungsempfehlungen</p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 mb-6">
        <p className="text-sm text-slate-700 leading-relaxed mb-3">{summary}</p>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-3">
            <p className="text-xs text-slate-500 mb-1">Gesamtinvestition</p>
            <p className="text-lg font-bold text-slate-900">
              {total_estimated_cost_eur[0].toLocaleString()}-{total_estimated_cost_eur[1].toLocaleString()}€
            </p>
          </div>
          <div className="bg-white rounded-lg p-3">
            <p className="text-xs text-slate-500 mb-1">Risikoreduktion</p>
            <p className="text-lg font-bold text-green-600">
              bis zu {estimated_risk_reduction_percent}%
            </p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-3">
        {allActions.map((action, index) => {
          const isExpanded = expandedAction === index;

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="border border-slate-200 rounded-xl overflow-hidden hover:shadow-md transition-all"
            >
              {/* Action Header - Always Visible */}
              <div
                className="p-4 cursor-pointer hover:bg-slate-50 transition-colors"
                onClick={() => setExpandedAction(isExpanded ? null : index)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-xl">{getCategoryIcon(action.category)}</span>
                      <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${getPriorityColor(action.priority)}`}>
                        {action.priority}
                      </span>
                      <span className="text-xs text-amber-500" title={`Dringlichkeit: ${action.urgency_score}/10`}>
                        {getUrgencyStars(action.urgency_score)}
                      </span>
                    </div>
                    <h4 className="font-bold text-slate-900 mb-1">{action.title}</h4>
                    <p className="text-xs text-slate-600">{action.description}</p>

                    {/* Quick Info */}
                    <div className="flex flex-wrap gap-3 mt-3">
                      <div className="flex items-center text-xs text-slate-600">
                        <Euro className="w-3 h-3 mr-1 text-green-600" />
                        <span className="font-semibold">
                          {action.estimated_cost_eur[0].toLocaleString()}-{action.estimated_cost_eur[1].toLocaleString()}€
                        </span>
                      </div>
                      <div className="flex items-center text-xs text-slate-600">
                        <Clock className="w-3 h-3 mr-1 text-blue-600" />
                        <span>{action.time_to_implement}</span>
                      </div>
                      {action.diy_possible && (
                        <span className="px-2 py-0.5 bg-green-50 text-green-700 text-xs font-medium rounded-full">
                          DIY möglich
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Expand Icon */}
                  <div className="ml-4">
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Action Details - Expandable */}
              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="border-t border-slate-200 p-4 bg-slate-50"
                >
                  {/* ROI */}
                  <div className="mb-4">
                    <p className="text-xs font-semibold text-slate-700 mb-1 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-1 text-green-500" />
                      Return on Investment:
                    </p>
                    <p className="text-sm text-slate-600">{action.roi_description}</p>
                  </div>

                  {/* Providers */}
                  {action.providers && action.providers.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-slate-700 mb-2">Benötigte Dienstleister:</p>
                      <div className="flex flex-wrap gap-2">
                        {action.providers.map((provider, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-white text-slate-700 text-xs rounded-lg border border-slate-200"
                          >
                            {provider}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Resources */}
                  {action.resources && action.resources.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-slate-700 mb-2">Weiterführende Ressourcen:</p>
                      <ul className="space-y-1">
                        {action.resources.map((resource, idx) => (
                          <li key={idx} className="text-xs text-slate-600 flex items-start">
                            <span className="text-blue-500 mr-2">📘</span>
                            <span>{resource}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start">
        <AlertCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-green-900">
          <strong>Priorisierung:</strong> Beginnen Sie mit "Sofort"-Maßnahmen. Diese bieten den größten Sicherheitsgewinn.
          Viele Maßnahmen amortisieren sich durch eingesparte Versicherungskosten und vermiedene Schäden.
        </div>
      </div>
    </motion.div>
  );
}

ActionPlanCard.propTypes = {
  data: PropTypes.shape({
    immediate_actions: PropTypes.array,
    short_term_actions: PropTypes.array,
    medium_term_actions: PropTypes.array,
    long_term_actions: PropTypes.array,
    total_estimated_cost_eur: PropTypes.arrayOf(PropTypes.number),
    estimated_risk_reduction_percent: PropTypes.number,
    summary: PropTypes.string,
  }),
};
