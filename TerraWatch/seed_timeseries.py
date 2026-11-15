import numpy as np
import rasterio
import xarray as xr
from backend.config import DETRENDED_TIF, TIMESERIES_NC

with rasterio.open(DETRENDED_TIF) as src:
    data = src.read(1)
    xs, _ = rasterio.transform.xy(src.transform, np.zeros(src.width), np.arange(src.width))
    _, ys = rasterio.transform.xy(src.transform, np.arange(src.height), np.zeros(src.height))

da = xr.DataArray(
    data[np.newaxis, :, :],
    dims=("time", "y", "x"),
    coords={
        "time": [np.datetime64("2026-10-11")],
        "y": np.array(ys),
        "x": np.array(xs),
    },
    name="vertical_cm",
)
da.to_netcdf(TIMESERIES_NC, encoding={"vertical_cm": {"zlib": True, "complevel": 5}})
print(f"Created {TIMESERIES_NC} ({TIMESERIES_NC.stat().st_size / 1024:.1f} KB) successfully!")
