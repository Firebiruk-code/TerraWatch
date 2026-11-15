import numpy as np
from backend.config import HIGH_SINKING_CM, MODERATE_SINKING_CM, UPLIFT_THRESHOLD_CM

def classify_risk(cell_cm: float) -> str:
    if cell_cm <= HIGH_SINKING_CM:
        return "High Subsidence Alert"
    if cell_cm <= MODERATE_SINKING_CM:
        return "Moderate Ground Sinking"
    if cell_cm >= UPLIFT_THRESHOLD_CM:
        return "Ground Uplift / Swelling"
    return "Stable Ground"

def build_forecast(mean_12d_cm: float, std_12d_cm: float, num_passes: int = 1, months: int = 6):
    cycles_per_year = 365.25 / 12.0
    annual_rate = round(mean_12d_cm * cycles_per_year, 2)
    se_12d = std_12d_cm / np.sqrt(max(1, num_passes))

    if num_passes < 5:
        confidence = f"Low Long-Term Confidence (12-Day Nowcast • N={num_passes} Pass)"
    elif num_passes < 30:
        confidence = f"Moderate Confidence (Seasonal Baseline Forming • N={num_passes} Passes)"
    else:
        confidence = f"High Confidence (Multi-Year Trend Validated • N={num_passes} Passes)"

    trajectory = []
    for m in range(0, months + 1):
        cycles = (m * 30.44) / 12.0
        est = mean_12d_cm * cycles
        sigma = np.sqrt((se_12d * cycles) ** 2 + (std_12d_cm * np.sqrt(max(0.5, cycles))) ** 2)
        trajectory.append({
            "month": m,
            "predicted_cm": round(est, 2),
            "upper_1s": round(est + sigma, 2),
            "lower_1s": round(est - sigma, 2),
            "upper_2s": round(est + 2 * sigma, 2),
            "lower_2s": round(est - 2 * sigma, 2),
        })

    return annual_rate, confidence, trajectory
