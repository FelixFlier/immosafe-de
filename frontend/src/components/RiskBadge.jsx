/**
 * RiskBadge Component
 * Displays a color-coded risk score badge
 * Green (<30), Yellow (<60), Red (≥60)
 */
import PropTypes from 'prop-types';

export default function RiskBadge({ score, level }) {
  const getColorClasses = () => {
    if (score < 30) {
      return 'bg-green-100 text-green-800 border-green-300';
    } else if (score < 60) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    } else {
      return 'bg-red-100 text-red-800 border-red-300';
    }
  };

  return (
    <div
      className={`inline-flex flex-col items-center justify-center px-6 py-4 rounded-2xl border-2 ${getColorClasses()}`}
    >
      <span className="text-4xl font-bold">{score}</span>
      <span className="text-sm font-medium uppercase tracking-wide mt-1">
        {level || 'Risk Score'}
      </span>
    </div>
  );
}

RiskBadge.propTypes = {
  score: PropTypes.number.isRequired,
  level: PropTypes.string,
};
