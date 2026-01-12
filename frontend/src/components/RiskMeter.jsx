/**
 * RiskMeter Component
 * Sleek, modern progress ring gauge with elegant design
 */
import PropTypes from 'prop-types';

/**
 * Get color configuration based on risk level
 */
function getRiskColors(level) {
  switch (level?.toLowerCase()) {
    case 'low':
      return { 
        primary: '#10b981', 
        secondary: '#34d399',
        gradient: 'from-emerald-400 to-emerald-600',
        glow: 'rgba(16, 185, 129, 0.3)'
      };
    case 'medium':
      return { 
        primary: '#f59e0b', 
        secondary: '#fbbf24',
        gradient: 'from-amber-400 to-amber-600',
        glow: 'rgba(245, 158, 11, 0.3)'
      };
    case 'high':
      return { 
        primary: '#ef4444', 
        secondary: '#f87171',
        gradient: 'from-red-400 to-red-600',
        glow: 'rgba(239, 68, 68, 0.3)'
      };
    default:
      return { 
        primary: '#6b7280', 
        secondary: '#9ca3af',
        gradient: 'from-slate-400 to-slate-600',
        glow: 'rgba(107, 114, 128, 0.3)'
      };
  }
}

export default function RiskMeter({ score = 0, level = 'low' }) {
  const colors = getRiskColors(level);
  
  // SVG circle calculations
  const size = 180;
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * Math.PI; // Semi-circle
  const progress = (score / 100) * circumference;
  
  // Center coordinates
  const center = size / 2;

  return (
    <div className="relative flex flex-col items-center">
      {/* SVG Gauge */}
      <div className="relative">
        <svg 
          width={size} 
          height={size / 2 + 20} 
          className="overflow-visible"
        >
          <defs>
            {/* Gradient for the progress arc */}
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={colors.secondary} />
              <stop offset="100%" stopColor={colors.primary} />
            </linearGradient>
            
            {/* Glow effect */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>

            {/* Track gradient - subtle */}
            <linearGradient id="trackGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#e2e8f0" />
              <stop offset="50%" stopColor="#f1f5f9" />
              <stop offset="100%" stopColor="#e2e8f0" />
            </linearGradient>
          </defs>

          {/* Background track - thin and elegant */}
          <path
            d={`M ${strokeWidth / 2 + 10} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2 - 10} ${center}`}
            fill="none"
            stroke="url(#trackGradient)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Progress arc */}
          <path
            d={`M ${strokeWidth / 2 + 10} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2 - 10} ${center}`}
            fill="none"
            stroke="url(#progressGradient)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            filter="url(#glow)"
            style={{
              transition: 'stroke-dashoffset 1s ease-out',
            }}
          />

          {/* End cap indicator */}
          <circle
            cx={strokeWidth / 2 + 10 + progress / circumference * (size - strokeWidth - 20)}
            cy={center - Math.sin(progress / circumference * Math.PI) * radius}
            r={6}
            fill={colors.primary}
            stroke="white"
            strokeWidth={3}
            filter="url(#glow)"
            style={{
              transition: 'all 1s ease-out',
            }}
          />

          {/* Scale labels */}
          <text x="15" y={center + 25} fontSize="11" fill="#94a3b8" fontWeight="500" textAnchor="start">0</text>
          <text x={center} y="15" fontSize="11" fill="#94a3b8" fontWeight="500" textAnchor="middle">50</text>
          <text x={size - 15} y={center + 25} fontSize="11" fill="#94a3b8" fontWeight="500" textAnchor="end">100</text>
        </svg>

        {/* Score Display - Centered in the gauge */}
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
          <div className="text-center">
            {/* Large Score Number */}
            <div className="relative">
              <span 
                className="text-6xl font-extrabold tracking-tight"
                style={{ color: colors.primary }}
              >
                {score}
              </span>
              <span className="text-xl font-medium text-slate-400 ml-1">/100</span>
            </div>
            
            {/* Risk Level Label */}
            <div className="mt-1">
              <span className="text-sm font-bold uppercase tracking-wider text-slate-500">
                {level || 'Unknown'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

RiskMeter.propTypes = {
  score: PropTypes.number,
  level: PropTypes.oneOf(['low', 'medium', 'high', 'Low', 'Medium', 'High']),
};
