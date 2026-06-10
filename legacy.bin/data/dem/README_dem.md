# DEM — Vermont QL1 LiDAR Elevation Data

## Source

Vermont Agency of Natural Resources — 2023 Statewide LiDAR Campaign  
Quality Level 1 (QL1) — 35cm resolution DEM

**URL:**
```
https://s3.us-east-2.amazonaws.com/vtopendata-prd/_Other/Projects/2023_Lidar/PreliminaryData/Statewide_2023_35cm_DEMHF.tif
```

## Usage

The DEM is accessed remotely via `rasterio` using a windowed read — only the
bounding box around the Stowe network is pulled (approx. 6km × 6km).

Run from your local machine (requires internet access to the Vermont S3 bucket):

```bash
python scripts/stage2a_dem.py
```

Outputs to `data/processed/`:
- `nodes_dem.geojson` — nodes with LiDAR-validated elevations
- `edges_dem.geojson` — edges with true 3D lengths
- `edges_dem.csv`
- `network_report.txt`

## Why This File Is Not Committed

The full GeoTIFF is statewide and very large. Only windowed/sampled data
is used. The processed outputs (nodes_dem.geojson, edges_dem.geojson) should
be committed after running locally.

## Reference

- ArcGIS Pro tool: https://pro.arcgis.com/en/pro-app/3.4/tool-reference/3d-analyst/add-z-information.htm
- VT Open Geodata Portal: https://geodata.vermont.gov
