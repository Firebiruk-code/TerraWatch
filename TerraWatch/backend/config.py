from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
DATA_FINAL = PROJECT_ROOT / "data" / "final"

DETRENDED_TIF = DATA_FINAL / "addis_ababa_vertical_detrended.tif"
RAW_VERT_TIF = DATA_FINAL / "addis_ababa_vertical_displacement_cm.tif"
SUBCITY_RISK_GEOJSON = DATA_FINAL / "addis_subcity_risk.geojson"
RISK_STRUCTURES_GEOJSON = DATA_FINAL / "addis_at_risk_structures.geojson"
SYNC_LOG_JSON = DATA_FINAL / "processed_granules.json"
TIMESERIES_NC = DATA_FINAL / "addis_timeseries.nc"

# Addis Ababa WGS84 Bounding Box: (min_lon, min_lat, max_lon, max_lat)
ADDIS_BBOX_WGS84 = (38.64, 8.83, 38.92, 9.11)
# Addis Ababa UTM Zone 37N Bounding Box (meters)
ADDIS_BBOX_UTM = (462000, 975000, 492000, 1008000)

# NISAR & Risk Thresholds (cm over 12-day repeat cycle)
HIGH_SINKING_CM = -0.50
MODERATE_SINKING_CM = -0.25
UPLIFT_THRESHOLD_CM = 0.30
COLOR_LIMIT_CM = 1.50
RADAR_RESOLUTION_M = 80

# Optional Gemini API key for live AI chat (falls back to built-in geotechnical engine if unset)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
