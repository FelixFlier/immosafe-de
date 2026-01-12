/**
 * RainfallChart Component
 * High-end bar chart with professional styling, gradient bars, and sleek tooltips
 */
import PropTypes from 'prop-types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from 'recharts';

/**
 * Custom premium tooltip component
 */
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const value = payload[0].value;
    return (
      <div className="bg-white px-4 py-3 shadow-xl rounded-xl border border-slate-100 min-w-[120px]">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
          {label}
        </p>
        <div className="flex items-baseline space-x-1">
          <span className="text-2xl font-bold text-slate-900">
            {value.toFixed(1)}
          </span>
          <span className="text-sm font-medium text-slate-500">mm</span>
        </div>
        <div className="mt-2 pt-2 border-t border-slate-100">
          <span className={`text-xs font-medium ${
            value >= 15 ? 'text-red-600' : 
            value >= 8 ? 'text-amber-600' : 
            value >= 2 ? 'text-blue-600' : 
            'text-slate-500'
          }`}>
            {value >= 15 ? '⚠️ Heavy rainfall' : 
             value >= 8 ? '🌧️ Moderate rainfall' : 
             value >= 2 ? '💧 Light rainfall' : 
             '☀️ Minimal rainfall'}
          </span>
        </div>
      </div>
    );
  }
  return null;
}

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
  label: PropTypes.string,
};

/**
 * RainfallChart component that visualizes daily rainfall data
 */
export default function RainfallChart({ data = [], isLocked = true, title = 'Historical Rain (7 Days)' }) {
  // Transform data array to recharts format with day labels
  const chartData = data.map((value, index) => {
    const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const dayIndex = (new Date().getDay() - (data.length - index) + 7) % 7;
    return {
      day: dayLabels[dayIndex] || `D${index + 1}`,
      rainfall: value ?? 0,
    };
  });

  // Fallback data if no real data provided
  const displayData = chartData.length > 0 ? chartData : [
    { day: 'Mon', rainfall: 2.5 },
    { day: 'Tue', rainfall: 0 },
    { day: 'Wed', rainfall: 8.2 },
    { day: 'Thu', rainfall: 15.1 },
    { day: 'Fri', rainfall: 3.4 },
    { day: 'Sat', rainfall: 0.5 },
    { day: 'Sun', rainfall: 12.0 },
  ];

  // Professional desaturated blue gradient colors based on intensity
  const getBarColor = (value) => {
    if (value >= 15) return '#334155'; // Slate-700 for heavy
    if (value >= 8) return '#475569';  // Slate-600 for moderate
    if (value >= 2) return '#64748b';  // Slate-500 for light
    return '#94a3b8';                  // Slate-400 for minimal
  };

  return (
    <div className="mb-6">
      {/* Chart Title */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {!isLocked && (
          <span className="text-xs text-slate-400">
            {displayData.reduce((sum, d) => sum + d.rainfall, 0).toFixed(1)} mm total
          </span>
        )}
      </div>

      {/* Chart Container */}
      <div 
        className={`
          relative bg-slate-50/50 rounded-xl p-4 border border-slate-100
          ${isLocked ? 'blur-md pointer-events-none' : ''}
        `}
      >
        <ResponsiveContainer width="100%" height={120}>
          <BarChart 
            data={displayData} 
            margin={{ top: 10, right: 10, left: -15, bottom: 0 }}
          >
            {/* Subtle horizontal grid lines only */}
            <CartesianGrid 
              strokeDasharray="3 3" 
              vertical={false} 
              stroke="#e2e8f0"
              strokeOpacity={0.6}
            />
            
            {/* X Axis - clean, no lines */}
            <XAxis 
              dataKey="day" 
              tick={{ fontSize: 11, fill: '#64748b', fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              dy={5}
            />
            
            {/* Y Axis - clean, no lines */}
            <YAxis 
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) => `${value}`}
              width={30}
            />
            
            {/* Premium Tooltip */}
            {!isLocked && (
              <Tooltip 
                content={<CustomTooltip />} 
                cursor={{ fill: 'rgba(148, 163, 184, 0.1)', radius: 4 }}
                wrapperStyle={{ outline: 'none' }}
              />
            )}
            
            {/* Bars with rounded tops and professional colors */}
            <Bar 
              dataKey="rainfall" 
              radius={[6, 6, 0, 0]} 
              maxBarSize={32}
            >
              {displayData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getBarColor(entry.rainfall)}
                  className="transition-all duration-200 hover:opacity-80"
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

RainfallChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.number),
  isLocked: PropTypes.bool,
  title: PropTypes.string,
};
