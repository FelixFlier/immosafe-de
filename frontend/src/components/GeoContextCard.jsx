/**
 * GeoContextCard Component
 * Displays geographical risk context: rivers, flood plains, wildfire zones, coastal areas
 */
import { motion } from 'framer-motion';
import { Waves, Flame, Wind, Mountain, MapPin, AlertTriangle, CheckCircle } from 'lucide-react';
import PropTypes from 'prop-types';

function RiverProximityBadge({ river }) {
  if (!river) return null;
  const isClose = river.distance_km < 2;
  const isNear = river.distance_km < 5;
  const color = isClose ? 'text-red-700 bg-red-50 border-red-200' :
    isNear ? 'text-amber-700 bg-amber-50 border-amber-200' :
      'text-slate-600 bg-slate-50 border-slate-200';

  return (
    <div className={`flex items-center space-x-3 px-4 py-3 rounded-xl border ${color}`}>
      <Waves className="w-4 h-4 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-bold uppercase tracking-wide">Nächster Fluss</p>
        <p className="text-sm font-semibold truncate">{river.name}</p>
      </div>
      <span className="text-sm font-bold whitespace-nowrap">{river.distance_km.toFixed(1)} km</span>
    </div>
  );
}

function ZoneBadge({ icon: Icon, label, detail, multiplier, active, colorClass }) {
  if (!active) return (
    <div className="flex items-center space-x-3 px-4 py-3 rounded-xl border border-slate-100 bg-slate-50 text-slate-400">
      <Icon className="w-4 h-4 flex-shrink-0" />
      <div className="flex-1">
        <p className="text-xs font-bold uppercase tracking-wide">{label}</p>
        <p className="text-xs">Kein erhöhtes Risiko</p>
      </div>
      <CheckCircle className="w-4 h-4 text-emerald-400" />
    </div>
  );

  return (
    <div className={`flex items-center space-x-3 px-4 py-3 rounded-xl border ${colorClass}`}>
      <AlertTriangle className="w-4 h-4 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-bold uppercase tracking-wide">{label}</p>
        <p className="text-sm font-semibold truncate">{detail}</p>
      </div>
      {multiplier && (
        <span className="text-xs font-bold whitespace-nowrap">
          ×{multiplier.toFixed(1)} Risiko
        </span>
      )}
    </div>
  );
}

function HistoricalEventsList({ historicalContext }) {
  if (!historicalContext) return null;

  const entries = Object.entries(historicalContext).filter(
    ([, ctx]) => ctx && ctx.summary
  );

  if (entries.length === 0) return null;

  return (
    <div className="mt-4">
      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center">
        <Mountain className="w-3.5 h-3.5 mr-1.5" />
        Historische Ereignisse
      </h4>
      <div className="space-y-2">
        {entries.map(([type, ctx]) => {
          const icons = { flood: '🌊', storm: '🌪️', earthquake: '🏔️' };
          return (
            <div key={type} className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-3">
              <p className="text-xs text-blue-900">{icons[type] || '⚠️'} {ctx.summary}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function GeoContextCard({ geoAnalysis, historicalContext }) {
  if (!geoAnalysis) return null;

  const { nearest_river, flood_plain, wildfire_zone, coastal, elevation_context } = geoAnalysis;

  const floodPlainActive = flood_plain?.in_flood_plain;
  const wildfireActive = wildfire_zone?.in_wildfire_zone;
  const coastalActive = coastal?.is_coastal;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-center space-x-2 mb-4">
        <MapPin className="w-4 h-4 text-primary-600" />
        <h3 className="text-sm font-bold text-slate-800">Geografischer Kontext</h3>
      </div>

      {/* Elevation Category */}
      {elevation_context?.elevation_category && (
        <div className="mb-4 px-4 py-3 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wide">Geländekategorie</p>
              <p className="text-sm font-semibold text-slate-800">{elevation_context.elevation_category}</p>
            </div>
            {elevation_context.landslide_risk && (
              <span className="text-xs px-2 py-1 bg-orange-100 text-orange-700 border border-orange-200 rounded-full font-semibold">
                Hangrutsch-Risiko
              </span>
            )}
          </div>
          {elevation_context.description && (
            <p className="text-xs text-slate-500 mt-1">
              {elevation_context.description.split('|')[0].trim()}
            </p>
          )}
        </div>
      )}

      {/* Risk Zones Grid */}
      <div className="space-y-2">
        <RiverProximityBadge river={nearest_river} />

        <ZoneBadge
          icon={Waves}
          label="Überschwemmungsgebiet"
          detail={floodPlainActive ? `${flood_plain.name} (${flood_plain.distance_km?.toFixed(1)}km)` : ''}
          multiplier={floodPlainActive ? flood_plain.risk_multiplier : null}
          active={floodPlainActive}
          colorClass="text-blue-700 bg-blue-50 border-blue-200"
        />

        <ZoneBadge
          icon={Flame}
          label="Waldbrandgebiet"
          detail={wildfireActive ? `${wildfire_zone.name} (${wildfire_zone.distance_km?.toFixed(1)}km)` : ''}
          multiplier={wildfireActive ? wildfire_zone.risk_multiplier : null}
          active={wildfireActive}
          colorClass="text-orange-700 bg-orange-50 border-orange-200"
        />

        <ZoneBadge
          icon={Wind}
          label="Küstengebiet (Sturm)"
          detail={coastalActive ? `${coastal.name} (${coastal.distance_km?.toFixed(1)}km)` : ''}
          multiplier={coastalActive ? coastal.storm_multiplier : null}
          active={coastalActive}
          colorClass="text-cyan-700 bg-cyan-50 border-cyan-200"
        />
      </div>

      {/* Historical Events */}
      <HistoricalEventsList historicalContext={historicalContext} />
    </motion.div>
  );
}

GeoContextCard.propTypes = {
  geoAnalysis: PropTypes.shape({
    nearest_river: PropTypes.shape({
      name: PropTypes.string,
      distance_km: PropTypes.number,
    }),
    flood_plain: PropTypes.object,
    wildfire_zone: PropTypes.object,
    coastal: PropTypes.object,
    elevation_context: PropTypes.object,
  }),
  historicalContext: PropTypes.object,
};

RiverProximityBadge.propTypes = {
  river: PropTypes.shape({
    name: PropTypes.string,
    distance_km: PropTypes.number,
  }),
};

ZoneBadge.propTypes = {
  icon: PropTypes.elementType.isRequired,
  label: PropTypes.string.isRequired,
  detail: PropTypes.string,
  multiplier: PropTypes.number,
  active: PropTypes.bool,
  colorClass: PropTypes.string,
};

HistoricalEventsList.propTypes = {
  historicalContext: PropTypes.object,
};
