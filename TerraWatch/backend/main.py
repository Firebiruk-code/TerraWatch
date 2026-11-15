from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import PointAnalysisResponse, ChatRequest, ChatResponse
from services.radar_service import RadarService
from services.ml_service import SpatialMLService
from services.forecast_service import classify_risk, build_forecast
from services.structure_service import StructureService
from services.ai_advisor import generate_point_interpretation, answer_user_question
from workers.nasa_sync import load_sync_log, sync_all_new_nisar
from workers.scheduler import start_scheduler, stop_scheduler, get_next_run

radar_svc: RadarService | None = None
ml_svc: SpatialMLService | None = None
struct_svc: StructureService | None = None

def _initialize_services():
    global radar_svc, ml_svc, struct_svc
    radar_svc = RadarService()
    ml_svc = SpatialMLService(radar_svc.utm_data, radar_svc.utm_transform, radar_svc.utm_crs)
    struct_svc = StructureService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    _initialize_services()
    # Backfill any unseen historical NISAR passes on startup, then check every 3 days
    sync_all_new_nisar(reload_callback=_initialize_services)
    start_scheduler(sync_fn=lambda: sync_all_new_nisar(reload_callback=_initialize_services))
    yield
    stop_scheduler()

app = FastAPI(title="TerraWatch Addis Ababa InSAR API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/overlay")
def get_overlay():
    return radar_svc.get_overlay_payload()

@app.get("/api/structures")
def get_structures():
    return {
        "subcities": struct_svc.subcities_geojson,
        "at_risk_structures": struct_svc.structures_geojson,
        "top_priority_list": struct_svc.get_top_at_risk(limit=10),
    }

@app.get("/api/ml-clusters")
def get_ml_clusters():
    return {"subsidence_clusters": ml_svc.clusters}

@app.get("/api/analyze", response_model=PointAnalysisResponse)
def analyze_location(lat: float, lon: float):
    sample = radar_svc.sample_point(lat, lon)
    if sample is None:
        raise HTTPException(status_code=400, detail="Coordinates outside Addis Ababa coverage.")

    if not sample["coherent"]:
        return PointAnalysisResponse(
            status="No Radar Coherence",
            lat=round(lat, 5),
            lon=round(lon, 5),
            risk_level="Low Radar Coherence",
            confidence_level="N/A (Water, Canopy, or Active Earthworks)",
            ai_summary="Radar signal decorrelated at this exact cell. Click an adjacent paved road, bridge, or building block.",
        )

    cell_cm = sample["cell_cm"]
    mean_cm = sample["mean_cm"]
    std_cm = sample["std_cm"]
    anomaly_pct = ml_svc.get_pixel_anomaly_score(sample["row"], sample["col"])

    risk = classify_risk(cell_cm)
    num_passes = max(1, len(load_sync_log().get("ingested_dates", [])))
    annual_rate, confidence, forecast = build_forecast(mean_cm, std_cm, num_passes=num_passes)
    nearby = struct_svc.find_structures_near(lat, lon, radius_m=150.0)
    ai_text = generate_point_interpretation(cell_cm, std_cm, risk, anomaly_pct, nearby)

    return PointAnalysisResponse(
        status="OK",
        lat=round(lat, 5),
        lon=round(lon, 5),
        exact_80m_cell_cm=cell_cm,
        neighborhood_mean_cm=mean_cm,
        uncertainty_1sigma_cm=std_cm,
        annualized_rate_cm_yr=annual_rate,
        ml_anomaly_score_pct=anomaly_pct,
        risk_level=risk,
        confidence_level=confidence,
        ai_summary=ai_text,
        nearby_structures=nearby,
        forecast=forecast,
    )

@app.post("/api/chat", response_model=ChatResponse)
def chat_advisor(req: ChatRequest):
    ctx = None
    if req.lat is not None and req.lon is not None:
        try:
            ctx = analyze_location(req.lat, req.lon).model_dump()
        except Exception:
            ctx = None
    return ChatResponse(answer=answer_user_question(req.question, ctx))

@app.get("/api/sync-status")
def sync_status():
    log = load_sync_log()
    return {
        "last_checked": log.get("last_checked"),
        "ingested_granules": len(log.get("ingested_granules", [])),
        "total_passes_stored": max(1, len(log.get("ingested_dates", []))),
        "streaming_mode": log.get("streaming_mode"),
        "next_scheduled_sync": get_next_run(),
    }

@app.post("/api/sync-now")
def sync_now():
    return sync_all_new_nisar(reload_callback=_initialize_services)


import xarray as xr
from backend.config import TIMESERIES_NC

@app.get("/api/timeseries")
def get_pixel_timeseries(lat: float, lon: float):
    """Returns historical cumulative displacement across all stored passes at (lat, lon)."""
    sample = radar_svc.sample_point(lat, lon)
    if sample is None or not sample["coherent"]:
        return {"dates": [], "cumulative_cm": []}

    if not TIMESERIES_NC.exists():
        return {"dates": ["2026-10-11"], "cumulative_cm": [sample["cell_cm"]]}

    with xr.open_dataset(TIMESERIES_NC) as ds:
        series = ds["vertical_cm"].isel(y=sample["row"], x=sample["col"]).load()
        dates = [str(t)[:10] for t in series.time.values]
        cum_vals = [round(float(v), 2) for v in series.cumsum().values]
        return {"dates": dates, "cumulative_cm": cum_vals}
