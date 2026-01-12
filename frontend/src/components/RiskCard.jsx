/**
 * RiskCard Component
 * Premium data-driven dashboard display for risk analysis results
 */
import { useState } from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { FileDown, Loader2, Mountain, CloudRain, Calendar, TrendingDown } from 'lucide-react';
import RiskMeter from './RiskMeter';
import RainfallChart from './RainfallChart';

export default function RiskCard({ data, loading, address }) {
  const [isPremiumUnlocked, setIsPremiumUnlocked] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const formatRiskValue = (value) => {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    return `${value} pts`;
  };

  const handleDownloadPDF = async () => {
    if (!address) return;
    
    setIsDownloading(true);
    try {
      const response = await fetch(`http://localhost:8001/api/report?address=${encodeURIComponent(address)}`);
      
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
      alert('Failed to download report. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-8">
        <div className="flex justify-center">
          <div className="w-36 h-36 bg-slate-100 rounded-3xl"></div>
        </div>
        <div className="space-y-4">
          <div className="h-3 bg-slate-100 rounded-full w-1/3"></div>
          <div className="h-12 bg-slate-100 rounded-xl"></div>
          <div className="h-12 bg-slate-100 rounded-xl"></div>
          <div className="h-12 bg-slate-100 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const { risk_score, risk_level, details } = data;
  const { 
    elevation_meters, 
    risk_breakdown, 
    last_7_days_rainfall = [],
    forecast_daily = [],
  } = details || {};

  const handleUnlockClick = () => {
    setIsPremiumUnlocked(!isPremiumUnlocked);
  };

  const getRiskLevelStyles = () => {
    switch (risk_level?.toLowerCase()) {
      case 'low':
        return { 
          bg: 'bg-emerald-50', 
          text: 'text-emerald-700', 
          border: 'border-emerald-200',
          dot: 'bg-emerald-500'
        };
      case 'medium':
        return { 
          bg: 'bg-amber-50', 
          text: 'text-amber-700', 
          border: 'border-amber-200',
          dot: 'bg-amber-500'
        };
      case 'high':
        return { 
          bg: 'bg-red-50', 
          text: 'text-red-700', 
          border: 'border-red-200',
          dot: 'bg-red-500'
        };
      default:
        return { 
          bg: 'bg-slate-50', 
          text: 'text-slate-700', 
          border: 'border-slate-200',
          dot: 'bg-slate-500'
        };
    }
  };

  const levelStyles = getRiskLevelStyles();

  // Risk breakdown items with icons
  const riskItems = [
    { 
      key: 'elevation_risk',
      label: 'Elevation Risk', 
      value: risk_breakdown?.elevation_risk,
      icon: Mountain,
      description: 'Based on property altitude'
    },
    { 
      key: 'terrain_valley_risk',
      label: 'Terrain & Valley', 
      value: risk_breakdown?.terrain_valley_risk,
      icon: TrendingDown,
      description: 'Topographical analysis'
    },
    { 
      key: 'historical_risk',
      label: 'Historical Rainfall', 
      value: risk_breakdown?.historical_risk,
      icon: CloudRain,
      description: 'Last 7 days precipitation'
    },
    { 
      key: 'forecast_risk',
      label: 'Weather Forecast', 
      value: risk_breakdown?.forecast_risk,
      icon: Calendar,
      description: '3-day rain prediction'
    },
  ];

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 15,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 15
      }
    }
  };

  return (
    <motion.div 
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* SECTION: Risk Assessment */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <section>
        {/* Section Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Risk Assessment
          </h2>
          <button
            onClick={handleDownloadPDF}
            disabled={isDownloading || !address}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-800 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed text-xs font-semibold uppercase tracking-wide"
            title="Download PDF Report"
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Generating</span>
              </>
            ) : (
              <>
                <FileDown className="w-3.5 h-3.5" />
                <span>Export</span>
              </>
            )}
          </button>
        </div>

        {/* Risk Meter */}
        <div className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-2xl p-6 border border-slate-200/60">
          <RiskMeter score={risk_score} level={risk_level} />
          <div className="text-center mt-5">
            <span className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-bold ${levelStyles.bg} ${levelStyles.text} border ${levelStyles.border}`}>
              <span className={`w-2 h-2 rounded-full ${levelStyles.dot} animate-pulse`}></span>
              <span>{risk_level || 'Unknown'} Risk Level</span>
            </span>
          </div>
        </div>

        {/* Elevation Highlight Card */}
        <div className="mt-4 bg-white rounded-xl p-4 border border-slate-200 flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl flex items-center justify-center">
            <Mountain className="w-6 h-6 text-slate-600" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Property Elevation</p>
            <p className="text-2xl font-bold text-slate-900 tracking-tight">
              {elevation_meters !== null && elevation_meters !== undefined 
                ? `${elevation_meters.toFixed(1)}m` 
                : 'N/A'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">Above sea level</p>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* SECTION: Property Insights */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <section>
        {/* Section Header */}
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">
          Property Insights
        </h2>

        {/* Risk Breakdown List - Data Rows Style */}
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          {riskItems.map((item, index) => {
            const Icon = item.icon;
            const isLast = index === riskItems.length - 1;
            
            return (
              <div 
                key={item.key}
                className={`flex items-center justify-between py-4 px-5 ${
                  !isLast ? 'border-b border-slate-100' : ''
                } hover:bg-slate-50/50 transition-colors duration-150`}
              >
                {/* Left: Icon + Label */}
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-4 h-4 text-slate-500" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-700">{item.label}</p>
                    <p className="text-xs text-slate-400">{item.description}</p>
                  </div>
                </div>
                
                {/* Right: Value */}
                <div className="text-right">
                  <span className="inline-block px-3 py-1.5 bg-slate-900 text-white text-sm font-bold rounded-lg">
                    {formatRiskValue(item.value)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* SECTION: Premium Insights */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <section className="relative">
        <h2 className={`text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 ${
          !isPremiumUnlocked ? 'blur-sm' : ''
        }`}>
          Weather Analysis
        </h2>

        <div className={!isPremiumUnlocked ? 'blur-sm' : ''}>
          <RainfallChart 
            data={last_7_days_rainfall} 
            isLocked={!isPremiumUnlocked}
            title="Historical Rain (Last 7 Days)"
          />
          <RainfallChart 
            data={forecast_daily}
            isLocked={!isPremiumUnlocked}
            title="3-Day Forecast"
          />
        </div>

        {/* Premium Lock Overlay - Frosted Glass */}
        {!isPremiumUnlocked && (
          <div className="absolute inset-0 flex items-center justify-center backdrop-blur-md bg-white/30 border border-white/40 rounded-2xl shadow-inner">
            <div className="text-center p-6">
              {/* Premium Badge */}
              <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-amber-400 to-amber-600 rounded-2xl shadow-lg shadow-amber-500/30 mb-4">
                <span className="text-2xl">👑</span>
              </div>
              
              {/* Unlock Button with Shine Effect */}
              <button 
                onClick={handleUnlockClick}
                className="relative overflow-hidden bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 hover:from-slate-900 hover:via-slate-800 hover:to-slate-900 text-white font-bold py-4 px-8 rounded-xl shadow-xl shadow-slate-900/30 transition-all duration-300 group hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
              >
                {/* Shine animation overlay */}
                <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12"></div>
                
                <span className="relative flex items-center space-x-3">
                  <span className="text-lg">🔓</span>
                  <span className="uppercase tracking-widest text-sm">Unlock Premium</span>
                </span>
              </button>
              
              <p className="text-xs text-slate-600 mt-4 font-medium">
                Access detailed weather analytics & forecasts
              </p>
            </div>
          </div>
        )}

        {isPremiumUnlocked && (
          <button 
            onClick={handleUnlockClick}
            className="w-full mt-3 text-xs text-slate-400 hover:text-slate-600 transition-colors"
          >
            (Demo: Click to re-lock)
          </button>
        )}
      </section>
    </motion.div>
  );
}

RiskCard.propTypes = {
  data: PropTypes.shape({
    risk_score: PropTypes.number,
    risk_level: PropTypes.string,
    details: PropTypes.shape({
      elevation_meters: PropTypes.number,
      risk_breakdown: PropTypes.shape({
        elevation_risk: PropTypes.number,
        terrain_valley_risk: PropTypes.number,
        historical_risk: PropTypes.number,
        forecast_risk: PropTypes.number,
      }),
      last_7_days_rainfall: PropTypes.arrayOf(PropTypes.number),
      forecast_daily: PropTypes.arrayOf(PropTypes.number),
    }),
  }),
  loading: PropTypes.bool,
  address: PropTypes.string,
};
