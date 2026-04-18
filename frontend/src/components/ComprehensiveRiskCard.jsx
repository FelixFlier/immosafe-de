/**
 * ComprehensiveRiskCard Component
 * Main risk display component showing comprehensive natural disaster analysis
 */
import { useState } from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { FileDown, Loader2, ChevronDown, Shield, Crown } from 'lucide-react';
import RiskOverview from './RiskOverview';
import RiskCategoryCard from './RiskCategoryCard';
import RainfallChart from './RainfallChart';
import InsuranceCard from './InsuranceCard';
import BenchmarkCard from './BenchmarkCard';
import ActionPlanCard from './ActionPlanCard';
import GeoContextCard from './GeoContextCard';

export default function ComprehensiveRiskCard({ data, loading, address }) {
  // FREE ACCESS FOR TESTING LAUNCH - Set to true to unlock all premium features
  const [isPremiumUnlocked, setIsPremiumUnlocked] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const handleDownloadPDF = async () => {
    if (!address) return;
    
    setIsDownloading(true);
    try {
      const response = await fetch(`/api/report?address=${encodeURIComponent(address)}`);
      
      if (!response.ok) {
        throw new Error('Failed to generate report');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `ImmoSafe_Report_${address.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('PDF-Export konnte nicht generiert werden. Bitte versuchen Sie es später erneut.');
    } finally {
      setIsDownloading(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="flex justify-center py-8">
          <div className="flex flex-col items-center space-y-3">
            <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
            <p className="text-sm text-slate-500">Analysiere Naturkatastrophen-Risiken...</p>
          </div>
        </div>
        <div className="space-y-4">
          <div className="h-32 bg-slate-100 rounded-2xl"></div>
          <div className="h-24 bg-slate-100 rounded-xl"></div>
          <div className="h-24 bg-slate-100 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // Check if this is the new comprehensive format
  const isComprehensiveData = data.total_risk_score !== undefined;

  // If legacy format, show simplified view
  if (!isComprehensiveData) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
        <p className="text-amber-800 text-sm">
          Legacy-Datenformat erkannt. Bitte Backend aktualisieren.
        </p>
      </div>
    );
  }

  // Tab data
  const tabs = [
    { id: 'overview', label: 'Übersicht' },
    { id: 'categories', label: 'Risikokategorien' },
    { id: 'location', label: '📍 Standort' },
    { id: 'premium', label: '✨ Premium', isPremium: true },
    { id: 'weather', label: 'Wetter' },
  ];

  // Risk categories for the categories tab
  const riskCategories = [
    { key: 'flood_risk', data: data.flood_risk },
    { key: 'storm_risk', data: data.storm_risk },
    { key: 'temperature_risk', data: data.temperature_risk },
    { key: 'hail_risk', data: data.hail_risk },
    { key: 'fire_risk', data: data.fire_risk },
    { key: 'earthquake_risk', data: data.earthquake_risk },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header with Export */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Shield className="w-5 h-5 text-primary-600" />
          <h2 className="text-sm font-bold text-slate-700">
            Naturkatastrophen-Analyse
          </h2>
        </div>
        <button
          onClick={handleDownloadPDF}
          disabled={isDownloading || !address}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-800 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold uppercase tracking-wide"
          title="PDF-Bericht herunterladen"
        >
          {isDownloading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Lädt...</span>
            </>
          ) : (
            <>
              <FileDown className="w-3.5 h-3.5" />
              <span>Export</span>
            </>
          )}
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-slate-100 rounded-xl p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2 px-3 text-xs font-semibold rounded-lg transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[300px]">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <RiskOverview data={data} />
        )}

        {/* Categories Tab */}
        {activeTab === 'categories' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-3"
          >
            {riskCategories.map(({ key, data: categoryData }) => (
              <RiskCategoryCard
                key={key}
                category={categoryData}
                defaultExpanded={key === 'flood_risk'}
              />
            ))}
          </motion.div>
        )}

        {/* Location / Geo Context Tab */}
        {activeTab === 'location' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <GeoContextCard
              geoAnalysis={data.premium_features?.geo_analysis}
              historicalContext={data.premium_features?.historical_context}
            />
          </motion.div>
        )}

        {/* Premium Insights Tab */}
        {activeTab === 'premium' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="relative"
          >
            {!isPremiumUnlocked ? (
              /* Premium Lock Overlay */
              <div className="min-h-[400px] flex items-center justify-center">
                <div className="text-center p-8 max-w-md">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-amber-400 to-amber-600 rounded-3xl shadow-2xl shadow-amber-500/30 mb-6">
                    <Crown className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-3">
                    Premium Insights freischalten
                  </h3>
                  <p className="text-slate-600 mb-6 leading-relaxed">
                    Erhalten Sie Zugang zu wertvollen Expertendaten:
                  </p>
                  <ul className="text-left space-y-3 mb-8">
                    <li className="flex items-start text-sm text-slate-700">
                      <span className="text-green-500 mr-2 mt-0.5">✓</span>
                      <span><strong>Versicherungsanalyse</strong> mit konkreten Kosteneinschätzungen</span>
                    </li>
                    <li className="flex items-start text-sm text-slate-700">
                      <span className="text-green-500 mr-2 mt-0.5">✓</span>
                      <span><strong>Regionaler Vergleich</strong> mit Benchmarking-Daten</span>
                    </li>
                    <li className="flex items-start text-sm text-slate-700">
                      <span className="text-green-500 mr-2 mt-0.5">✓</span>
                      <span><strong>Maßnahmenplan</strong> mit priorisierten Handlungsempfehlungen</span>
                    </li>
                    <li className="flex items-start text-sm text-slate-700">
                      <span className="text-green-500 mr-2 mt-0.5">✓</span>
                      <span><strong>Finanzielle Impact-Analyse</strong> inkl. ROI-Berechnungen</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => setIsPremiumUnlocked(true)}
                    className="relative overflow-hidden bg-gradient-to-r from-amber-500 via-amber-600 to-orange-600 hover:from-amber-600 hover:via-amber-700 hover:to-orange-700 text-white font-bold py-4 px-8 rounded-2xl shadow-2xl transition-all duration-300 group hover:scale-[1.02] w-full"
                  >
                    <span className="relative flex items-center justify-center space-x-2">
                      <Crown className="w-5 h-5" />
                      <span className="uppercase tracking-widest text-sm">Jetzt Premium testen</span>
                    </span>
                  </button>
                  <p className="text-xs text-slate-500 mt-4">
                    Demo-Modus: Vollständiger Zugriff ohne Registrierung
                  </p>
                </div>
              </div>
            ) : (
              /* Premium Content */
              <div className="space-y-6">
                {/* Insurance Analysis */}
                {data.premium_features?.insurance_analysis && (
                  <InsuranceCard data={data.premium_features.insurance_analysis} />
                )}

                {/* Benchmark Analysis */}
                {data.premium_features?.benchmark_analysis && (
                  <BenchmarkCard data={data.premium_features.benchmark_analysis} />
                )}

                {/* Action Plan */}
                {data.premium_features?.action_plan && (
                  <ActionPlanCard data={data.premium_features.action_plan} />
                )}

                {/* Data Sources - Trust Building */}
                {data.premium_features?.data_sources && (
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-200 p-6">
                    <h4 className="text-sm font-bold text-slate-900 mb-4 flex items-center">
                      <Shield className="w-4 h-4 mr-2 text-blue-600" />
                      Datenquellen & Transparenz
                    </h4>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      {Object.entries(data.premium_features.data_sources).map(([key, value]) => {
                        if (key === 'data_quality_score' || key === 'last_updated') return null;
                        return (
                          <div key={key} className="bg-white rounded-lg p-3">
                            <p className="text-slate-500 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                            <p className="text-slate-900 font-semibold">{value}</p>
                          </div>
                        );
                      })}
                    </div>
                    <div className="mt-4 pt-4 border-t border-blue-200 flex justify-between text-xs">
                      <span className="text-slate-600">
                        Datenqualität: <strong className="text-green-600">{data.premium_features.data_sources.data_quality_score}%</strong>
                      </span>
                      <span className="text-slate-600">
                        Aktualisiert: <strong>{data.premium_features.data_sources.last_updated}</strong>
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}

        {/* Weather Data Tab (Premium) */}
        {activeTab === 'weather' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="relative"
          >
            <div className={!isPremiumUnlocked ? 'blur-sm' : ''}>
              <div className="space-y-4">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Niederschlagsanalyse
                </h3>
                
                {data.flood_details && (
                  <>
                    <RainfallChart 
                      data={data.flood_details.last_7_days_rainfall} 
                      isLocked={!isPremiumUnlocked}
                      title="Niederschlag (letzte 7 Tage)"
                    />
                    <RainfallChart 
                      data={data.flood_details.forecast_daily}
                      isLocked={!isPremiumUnlocked}
                      title="3-Tage Prognose"
                    />
                  </>
                )}

                {/* Additional Weather Stats */}
                <div className="bg-white rounded-xl border border-slate-200 p-4">
                  <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                    Klimadaten
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-500">95. Perzentil Regen:</span>
                      <span className="font-bold text-slate-800 ml-2">
                        {data.flood_details?.history_rain_95th_percentile_mm?.toFixed(1) || 'N/A'} mm
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Max. Tagesregen:</span>
                      <span className="font-bold text-slate-800 ml-2">
                        {data.flood_details?.history_rain_max_mm?.toFixed(1) || 'N/A'} mm
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">3-Tage Prognose:</span>
                      <span className="font-bold text-slate-800 ml-2">
                        {data.flood_details?.forecast_rain_3day_mm?.toFixed(1) || 'N/A'} mm
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Höhenlage:</span>
                      <span className="font-bold text-slate-800 ml-2">
                        {data.flood_details?.elevation_meters?.toFixed(0) || 'N/A'} m
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Premium Lock Overlay */}
            {!isPremiumUnlocked && (
              <div className="absolute inset-0 flex items-center justify-center backdrop-blur-md bg-white/30 border border-white/40 rounded-2xl">
                <div className="text-center p-6">
                  <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-amber-400 to-amber-600 rounded-2xl shadow-lg shadow-amber-500/30 mb-4">
                    <span className="text-2xl">👑</span>
                  </div>
                  
                  <button 
                    onClick={() => setIsPremiumUnlocked(true)}
                    className="relative overflow-hidden bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 hover:from-slate-900 hover:via-slate-800 hover:to-slate-900 text-white font-bold py-3 px-6 rounded-xl shadow-xl transition-all duration-300 group hover:shadow-2xl hover:scale-[1.02]"
                  >
                    <span className="relative flex items-center space-x-2">
                      <span>🔓</span>
                      <span className="uppercase tracking-widest text-xs">Premium freischalten</span>
                    </span>
                  </button>
                  
                  <p className="text-xs text-slate-600 mt-3">
                    Wetterdaten & historische Analyse
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

ComprehensiveRiskCard.propTypes = {
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
    flood_details: PropTypes.object,
  }),
  loading: PropTypes.bool,
  address: PropTypes.string,
};
