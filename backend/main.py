"""
ImmoSafe DE - FastAPI Backend
Production-ready API for comprehensive natural disaster risk analysis in Germany.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from services.external_api import GeoService, WeatherService
from services.risk_calculator import calculate_total_risk
from services.natural_disaster_service import NaturalDisasterService

# Load environment variables
load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AddressRequest(BaseModel):
    """Request model for address analysis."""
    address: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Address to analyze (German addresses preferred)",
        examples=["Marienplatz 1, 80331 München, Deutschland"],
    )


class CoordinatesResponse(BaseModel):
    """Geographic coordinates."""
    lat: float
    lng: float


class RiskCategory(BaseModel):
    """Individual risk category assessment."""
    name: str
    name_de: str
    icon: str
    score: int = Field(..., ge=0, le=100)
    level: str
    factors: list[str]
    recommendations: list[str]
    data: dict = {}


class FloodRiskDetails(BaseModel):
    """Detailed flood risk data."""
    elevation_meters: float
    history_rain_95th_percentile_mm: float
    history_rain_max_mm: float
    forecast_rain_3day_mm: float
    risk_breakdown: dict[str, int]
    last_7_days_rainfall: list[float] = []
    forecast_daily: list[float] = []
    relative_height_m: float = 0.0
    terrain_analysis_available: bool = False


class ComprehensiveAnalysisResponse(BaseModel):
    """Complete natural disaster risk analysis response."""
    address: str
    coordinates: CoordinatesResponse
    
    # Overall Assessment
    total_risk_score: int = Field(..., ge=0, le=100)
    total_risk_level: str
    primary_risks: list[str]
    
    # Individual Risk Categories
    flood_risk: RiskCategory
    storm_risk: RiskCategory
    fire_risk: RiskCategory
    temperature_risk: RiskCategory
    hail_risk: RiskCategory
    earthquake_risk: RiskCategory
    
    # Detailed flood data (for existing charts)
    flood_details: FloodRiskDetails
    
    # Metadata
    is_freemium_locked: bool = True
    analysis_version: str = "2.0"


# Legacy response model (for backwards compatibility)
class LegacyRiskDetails(BaseModel):
    """Legacy detailed risk analysis data."""
    elevation_meters: float
    history_rain_95th_percentile_mm: float
    history_rain_max_mm: float
    forecast_rain_3day_mm: float
    risk_breakdown: dict[str, int]
    last_7_days_rainfall: list[float] = []
    forecast_daily: list[float] = []
    relative_height_m: float = 0.0
    terrain_analysis_available: bool = False


class LegacyAnalysisResponse(BaseModel):
    """Legacy analysis response for backwards compatibility."""
    address: str
    coordinates: CoordinatesResponse
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    details: LegacyRiskDetails
    is_freemium_locked: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    maps_api_key = os.getenv("MAPS_API_KEY", "")
    if not maps_api_key:
        print("WARNING: MAPS_API_KEY is not configured. Some features may not work.")
    yield
    print("Application shutting down...")


app = FastAPI(
    title="ImmoSafe DE API",
    description="Umfassende Naturkatastrophen-Risikoanalyse für deutsche Immobilien",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root() -> dict:
    """Root endpoint - API health check."""
    return {
        "status": "online",
        "service": "ImmoSafe DE API",
        "version": "2.0.0",
        "message": "Willkommen bei der ImmoSafe DE API - Umfassende Naturkatastrophen-Risikoanalyse",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "checks": {
            "api": True,
            "maps_api_configured": bool(os.getenv("MAPS_API_KEY", "")),
        },
    }


@app.post("/api/analyze", response_model=ComprehensiveAnalysisResponse)
@limiter.limit("10/minute")
async def analyze_address(
    request: Request,
    body: AddressRequest,
) -> ComprehensiveAnalysisResponse:
    """
    Comprehensive natural disaster risk analysis for a German address.
    
    Analyzes:
    - 🌊 Flood risk (elevation, rainfall, terrain)
    - 🌪️ Storm/wind risk (historical gusts, frequency)
    - 🔥 Wildfire risk (temperature, drought patterns)
    - 🌡️ Extreme temperature risk (heat waves, frost)
    - ⚡ Thunderstorm/hail risk (heavy precipitation)
    - 🏔️ Earthquake risk (seismic zones)
    
    Returns comprehensive risk analysis with weighted total score.
    """
    try:
        # Initialize services
        geo_service = GeoService()
        weather_service = WeatherService()
        disaster_service = NaturalDisasterService()
        
        # Step 1: Geocode address
        coordinates = await geo_service.get_coordinates(body.address)
        lat, lng = coordinates["lat"], coordinates["lng"]
        
        # Step 2: Fetch all base data in parallel
        elevation_task = geo_service.get_elevation(lat, lng)
        flood_risk_task = weather_service.get_flood_risk_data(lat, lng)
        forecast_task = weather_service.get_current_forecast(lat, lng)
        terrain_task = geo_service.analyze_terrain(lat, lng)
        
        elevation, flood_data, forecast, terrain_data = await asyncio.gather(
            elevation_task, flood_risk_task, forecast_task, terrain_task
        )
        
        # Step 3: Calculate flood risk (existing logic)
        flood_result = calculate_total_risk(
            elevation=elevation,
            rainfall_95th=flood_data["rainfall_95th_percentile"],
            forecast_rain=forecast["precipitation_3day_sum"],
            relative_height=terrain_data["relative_height"],
            terrain_data_available=terrain_data["is_data_available"],
        )
        
        # Step 4: Analyze all natural disaster risks
        comprehensive = await disaster_service.analyze_all_risks(
            lat, lng,
            flood_data={
                "risk_score": flood_result["score"],
                "risk_level": flood_result["level"],
            }
        )
        
        # Build flood risk category
        flood_factors = []
        if elevation < 100:
            flood_factors.append(f"Niedrige Lage ({elevation:.0f}m über NN)")
        if flood_data["rainfall_95th_percentile"] > 20:
            flood_factors.append(f"Hohe historische Niederschläge (95. Perzentil: {flood_data['rainfall_95th_percentile']:.1f}mm)")
        if terrain_data["relative_height"] < 2:
            flood_factors.append("Lage in Senke oder Tal")
        if not flood_factors:
            flood_factors.append("Moderate Hochwassergefährdung")
        
        flood_recommendations = []
        if flood_result["score"] >= 50:
            flood_recommendations.extend([
                "Elementarschadenversicherung dringend empfohlen",
                "Hochwasserschutzmaßnahmen prüfen",
                "Rückstauklappe im Abwassersystem installieren",
            ])
        elif flood_result["score"] >= 30:
            flood_recommendations.append("Elementarschadenversicherung empfohlen")
        else:
            flood_recommendations.append("Standard-Gebäudeversicherung ausreichend")
        
        # Build response
        return ComprehensiveAnalysisResponse(
            address=body.address,
            coordinates=CoordinatesResponse(lat=lat, lng=lng),
            total_risk_score=comprehensive["total_risk_score"],
            total_risk_level=comprehensive["total_risk_level"],
            primary_risks=comprehensive["primary_risks"],
            
            flood_risk=RiskCategory(
                name="Flood",
                name_de="Hochwasser",
                icon="🌊",
                score=flood_result["score"],
                level=flood_result["level"],
                factors=flood_factors,
                recommendations=flood_recommendations,
                data={
                    "elevation_m": round(elevation, 1),
                    "relative_height_m": terrain_data["relative_height"],
                },
            ),
            
            storm_risk=RiskCategory(
                name="Storm",
                name_de="Sturm",
                icon="🌪️",
                score=comprehensive["storm_risk"]["storm_risk_score"],
                level=comprehensive["storm_risk"]["storm_risk_level"],
                factors=comprehensive["storm_risk"]["factors"],
                recommendations=comprehensive["storm_risk"]["recommendations"],
                data={
                    "max_gust_kmh": comprehensive["storm_risk"]["max_wind_gust_kmh"],
                    "storm_days_per_year": comprehensive["storm_risk"]["avg_annual_storm_days"],
                },
            ),
            
            fire_risk=RiskCategory(
                name="Fire",
                name_de="Waldbrand",
                icon="🔥",
                score=comprehensive["fire_risk"]["fire_risk_score"],
                level=comprehensive["fire_risk"]["fire_risk_level"],
                factors=comprehensive["fire_risk"]["factors"],
                recommendations=comprehensive["fire_risk"]["recommendations"],
                data={
                    "fire_weather_index": comprehensive["fire_risk"]["fire_weather_index"],
                    "drought_days": comprehensive["fire_risk"]["drought_days_per_year"],
                },
            ),
            
            temperature_risk=RiskCategory(
                name="Temperature",
                name_de="Extremtemperaturen",
                icon="🌡️",
                score=comprehensive["temperature_risk"]["temp_risk_score"],
                level=comprehensive["temperature_risk"]["temp_risk_level"],
                factors=comprehensive["temperature_risk"]["factors"],
                recommendations=comprehensive["temperature_risk"]["recommendations"],
                data={
                    "heat_days": comprehensive["temperature_risk"]["heat_wave_days_per_year"],
                    "frost_days": comprehensive["temperature_risk"]["frost_days_per_year"],
                },
            ),
            
            hail_risk=RiskCategory(
                name="Hail",
                name_de="Gewitter/Hagel",
                icon="⚡",
                score=comprehensive["hail_risk"]["hail_risk_score"],
                level=comprehensive["hail_risk"]["hail_risk_level"],
                factors=comprehensive["hail_risk"]["factors"],
                recommendations=comprehensive["hail_risk"]["recommendations"],
                data={
                    "heavy_precip_days": comprehensive["hail_risk"]["heavy_precip_days"],
                },
            ),
            
            earthquake_risk=RiskCategory(
                name="Earthquake",
                name_de="Erdbeben",
                icon="🏔️",
                score=comprehensive["earthquake_risk"]["earthquake_risk_score"],
                level=comprehensive["earthquake_risk"]["earthquake_risk_level"],
                factors=comprehensive["earthquake_risk"]["factors"],
                recommendations=comprehensive["earthquake_risk"]["recommendations"],
                data={
                    "zone": comprehensive["earthquake_risk"]["zone"],
                    "zone_name": comprehensive["earthquake_risk"]["zone_name"],
                },
            ),
            
            flood_details=FloodRiskDetails(
                elevation_meters=round(elevation, 2),
                history_rain_95th_percentile_mm=flood_data["rainfall_95th_percentile"],
                history_rain_max_mm=flood_data["max_daily_rainfall"],
                forecast_rain_3day_mm=forecast["precipitation_3day_sum"],
                risk_breakdown=flood_result["breakdown"],
                last_7_days_rainfall=flood_data["last_7_days_rainfall"],
                forecast_daily=forecast["precipitation_daily"],
                relative_height_m=terrain_data["relative_height"],
                terrain_analysis_available=terrain_data["is_data_available"],
            ),
            
            is_freemium_locked=True,
            analysis_version="2.0",
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"External service error: {str(e)}",
        )


# Legacy endpoint for backwards compatibility
@app.post("/api/analyze/legacy", response_model=LegacyAnalysisResponse)
@limiter.limit("10/minute")
async def analyze_address_legacy(
    request: Request,
    body: AddressRequest,
) -> LegacyAnalysisResponse:
    """Legacy flood-only analysis endpoint for backwards compatibility."""
    try:
        geo_service = GeoService()
        weather_service = WeatherService()
        
        coordinates = await geo_service.get_coordinates(body.address)
        lat, lng = coordinates["lat"], coordinates["lng"]
        
        elevation_task = geo_service.get_elevation(lat, lng)
        flood_risk_task = weather_service.get_flood_risk_data(lat, lng)
        forecast_task = weather_service.get_current_forecast(lat, lng)
        terrain_task = geo_service.analyze_terrain(lat, lng)
        
        elevation, flood_data, forecast, terrain_data = await asyncio.gather(
            elevation_task, flood_risk_task, forecast_task, terrain_task
        )
        
        risk_result = calculate_total_risk(
            elevation=elevation,
            rainfall_95th=flood_data["rainfall_95th_percentile"],
            forecast_rain=forecast["precipitation_3day_sum"],
            relative_height=terrain_data["relative_height"],
            terrain_data_available=terrain_data["is_data_available"],
        )
        
        return LegacyAnalysisResponse(
            address=body.address,
            coordinates=CoordinatesResponse(lat=lat, lng=lng),
            risk_score=risk_result["score"],
            risk_level=risk_result["level"],
            details=LegacyRiskDetails(
                elevation_meters=round(elevation, 2),
                history_rain_95th_percentile_mm=flood_data["rainfall_95th_percentile"],
                history_rain_max_mm=flood_data["max_daily_rainfall"],
                forecast_rain_3day_mm=forecast["precipitation_3day_sum"],
                risk_breakdown=risk_result["breakdown"],
                last_7_days_rainfall=flood_data["last_7_days_rainfall"],
                forecast_daily=forecast["precipitation_daily"],
                relative_height_m=terrain_data["relative_height"],
                terrain_analysis_available=terrain_data["is_data_available"],
            ),
            is_freemium_locked=True,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"External service error: {str(e)}",
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Ein unerwarteter Fehler ist aufgetreten.",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None,
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
