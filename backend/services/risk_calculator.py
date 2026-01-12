"""
ImmoSafe DE - Risk Calculator V3
Production-grade algorithm for calculating flood risk based on elevation, 
rainfall history, forecast, and terrain analysis with sink/valley detection.
"""

from typing import Literal, TypedDict, Union, Optional


RiskLevel = Literal["Low", "Medium", "High", "Critical"]


class RiskResult(TypedDict):
    """Risk calculation result."""
    score: int
    level: RiskLevel
    breakdown: dict[str, int]


def _safe_int(value: Union[int, float, None, str]) -> int:
    """
    Convert any value to a safe integer.
    Handles None, 'N/A' strings, floats, and already integers.
    
    Args:
        value: Any value to convert.
        
    Returns:
        Integer representation, or 0 if conversion fails.
    """
    if value is None:
        return 0
    if isinstance(value, str):
        if value.upper() in ("N/A", "NA", "NONE", "NULL", ""):
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    if isinstance(value, (int, float)):
        return int(value)
    return 0


def calculate_total_risk(
    elevation: float,
    rainfall_95th: float,
    forecast_rain: float,
    relative_height: Optional[float] = None,
    terrain_data_available: bool = False,
) -> RiskResult:
    """
    Calculate total flood risk score based on geographic, weather, and terrain factors.
    
    V3 Scoring Algorithm (Production Grade with Terrain Analysis):
    - Elevation risk: INCREASED WEIGHT (up to 40 points)
      - < 50m: 40 points (river valleys, coastal areas - extreme risk)
      - < 100m: 35 points (very low elevation)
      - < 200m: 25 points (lowland areas)
      - < 400m: 10 points (moderate elevation)
      - >= 400m: 0 points (highland - minimal flood risk)
      
    - Historical rain risk: Up to 30 points (formula: min(rain_mm * 1.5, 30))
      - Always calculates from available data, returns 0 if data missing
      
    - Forecast risk: Up to 35 points
      - > 50mm: 35 points (severe flooding expected)
      - > 40mm: 30 points (severe storm incoming)
      - > 20mm: 20 points (significant rain expected)
      - > 10mm: 10 points (moderate rain expected)
      - <= 10mm: 0 points (dry forecast)
    
    - Terrain/Sink Risk (NEW): Up to +40 or -10 points
      - relative_height < 1.0m: +40 points (CRITICAL - house is in a sink/valley)
      - relative_height > 5.0m: -10 points (bonus safety - house is on a hill)
    
    CRITICAL RISK RULE:
    If rainfall_95th > 40mm AND elevation < 100m => Force Critical Risk (Score >= 80)
    
    Args:
        elevation: Elevation in meters above sea level.
        rainfall_95th: 95th percentile of historical daily rainfall in mm.
        forecast_rain: Total forecasted rainfall for next 3 days in mm.
        relative_height: Height difference between center and local minimum (meters).
                        Positive = higher than surroundings, negative = lower.
        terrain_data_available: Whether terrain analysis data is available.
        
    Returns:
        RiskResult with score (0-100), level, and breakdown (all ints).
    """
    # Ensure inputs are valid floats (handle None/N/A)
    elevation = float(elevation) if elevation is not None else 0.0
    rainfall_95th = float(rainfall_95th) if rainfall_95th is not None else 0.0
    forecast_rain = float(forecast_rain) if forecast_rain is not None else 0.0
    
    score = 0
    breakdown: dict[str, int] = {}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ELEVATION RISK ASSESSMENT (INCREASED WEIGHT - Max 40 points)
    # Lower elevations are significantly more prone to flooding
    # ═══════════════════════════════════════════════════════════════════════════
    if elevation < 50:
        elevation_points = 40  # River valleys, coastal areas - extreme risk
    elif elevation < 100:
        elevation_points = 35  # Very low elevation - high risk
    elif elevation < 200:
        elevation_points = 25  # Lowland area - moderate-high risk
    elif elevation < 400:
        elevation_points = 10  # Moderate elevation - low risk
    else:
        elevation_points = 0   # Highland - minimal flood risk from elevation
    
    score += elevation_points
    breakdown["elevation_risk"] = _safe_int(elevation_points)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HISTORICAL RAINFALL PATTERN RISK (Max 30 points)
    # Uses formula: min(rainfall_95th * 1.5, 30) for consistent scoring
    # Always calculates from available data - returns 0 if data is missing
    # ═══════════════════════════════════════════════════════════════════════════
    history_points = min(int(rainfall_95th * 1.5), 30)
    
    score += history_points
    breakdown["history_risk"] = _safe_int(history_points)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FORECAST RISK - IMMINENT WEATHER THREATS (Max 35 points)
    # ═══════════════════════════════════════════════════════════════════════════
    if forecast_rain > 50:
        forecast_points = 35  # Severe flooding expected
    elif forecast_rain > 40:
        forecast_points = 30  # Severe storm incoming
    elif forecast_rain > 20:
        forecast_points = 20  # Significant rain expected
    elif forecast_rain > 10:
        forecast_points = 10  # Moderate rain expected
    else:
        forecast_points = 0   # Dry forecast
    
    score += forecast_points
    breakdown["forecast_risk"] = _safe_int(forecast_points)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TERRAIN/SINK RISK - NEW V3 FEATURE (Up to +40 or -10 points)
    # Detects if property is in a local sink/valley or on elevated ground
    # ═══════════════════════════════════════════════════════════════════════════
    terrain_points = 0
    if terrain_data_available and relative_height is not None:
        if relative_height < 1.0:
            # CRITICAL: Property is in a sink/valley - water accumulates here
            terrain_points = 40
            breakdown["terrain_risk"] = _safe_int(terrain_points)
        elif relative_height > 5.0:
            # BONUS: Property is on elevated ground - water drains away
            terrain_points = -10
            breakdown["terrain_bonus"] = _safe_int(abs(terrain_points))
        else:
            # Normal terrain - no adjustment
            breakdown["terrain_risk"] = 0
        
        score += terrain_points
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CRITICAL RISK DETECTION RULE
    # If history_rain_95th > 40mm AND elevation < 100m => Critical Risk (>= 80)
    # This catches dangerous combinations that might not score high individually
    # ═══════════════════════════════════════════════════════════════════════════
    critical_combination = rainfall_95th > 40 and elevation < 100
    if critical_combination and score < 80:
        # Boost score to critical threshold
        critical_boost = 80 - score
        score = 80
        breakdown["critical_boost"] = _safe_int(critical_boost)
    
    # Cap at 100 and floor at 0
    final_score = max(0, min(score, 100))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DETERMINE RISK LEVEL
    # ═══════════════════════════════════════════════════════════════════════════
    level: RiskLevel
    if final_score >= 70:
        level = "Critical"
    elif final_score >= 50:
        level = "High"
    elif final_score >= 25:
        level = "Medium"
    else:
        level = "Low"
    
    # Ensure all breakdown values are strictly integers
    sanitized_breakdown = {k: _safe_int(v) for k, v in breakdown.items()}
    
    return RiskResult(
        score=final_score,
        level=level,
        breakdown=sanitized_breakdown,
    )
