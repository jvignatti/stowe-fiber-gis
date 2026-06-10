# Stowe Fiber Network — GIS Analysis

**Resort:** Stowe Mountain Resort (Vail Resorts)  
**Department:** Mountain Operations / IT Infrastructure  
**Author:** JC Vignatti  
**Data vintage:** 2026  
**Coordinate system:** EPSG:4326 (WGS 84)

---

## Project Overview

This repository contains the complete GIS dataset, processing scripts, and documentation for the Stowe Mountain Resort fiber optic network. The project maps all 47 network nodes and 39 fiber segments across the full resort footprint — from the base village (Nordic Center, ~1,165 ft) to the upper mountain (Ski Patrol Spruce Side, ~3,609 ft).

The analysis supports three core business questions:

1. **What is the actual fiber length?** — True 3D length corrected for Stowe's 2,444 ft of vertical relief
2. **Own vs. lease cost analysis** — Financial case for eliminating the two leased segments
3. **Catastrophic failure scenario** — Operational and revenue impact if a critical segment is severed during peak operation

---

## Repository Structure

```
stowe-fiber-gis/
├── data/
│   ├── raw/                    # Source CSVs (nodes, edges, 3D variants)
│   ├── processed/              # GeoJSON, GeoPackage outputs
│   └── dem/                    # DEM instructions and local run notes
├── scripts/
│   ├── stage1_nodes_edges.py       # Build base node/edge dataset
│   ├── stage2a_dem.py              # LiDAR DEM elevation sampling (run locally)
│   ├── stage2b_estimated_elevation.py  # Estimated elevation (runs anywhere)
│   ├── stage3_carto_export.py      # CARTO-ready GeoJSON export
│   └── build_geodatabase.py        # Builds stowe_fiber_network.gpkg
├── docs/
│   ├── network_topology.md         # Full topology documentation
│   ├── CARTO_STYLE_GUIDE.md        # CARTO map configuration guide
│   └── recommendations.md          # Business analysis and recommendations
├── reports/
│   └── dashboard_summary.json      # Machine-readable summary stats
├── requirements.txt
└── .gitignore
```

---

## Network Summary

| Metric | Value |
|--------|-------|
| Total nodes | 47 |
| Active nodes | 35 |
| Total segments | 39 |
| **Total network length (3D)** | **41,475 ft / 7.86 miles** |
| Owned fiber | 31,390 ft |
| Leased fiber | 10,085 ft |
| Lift fiber | 16,045 ft |
| Buried owned | 15,346 ft |
| Elevation correction over 2D | +3.7% |
| Vertical range | 1,165 ft – 3,609 ft (2,444 ft) |
| Primary hubs | MOC, Spruce Camp, Admin |

---

## GeoPackage Layers (`stowe_fiber_network.gpkg`)

| Layer | Type | Features | Description |
|-------|------|----------|-------------|
| `fiber_nodes` | Point | 47 | All network nodes with elevation and status |
| `fiber_edges` | Line | 39 | All segments with 2D/3D lengths |
| `fiber_hubs` | Point | 3 | MOC, Spruce Camp, Admin |
| `fiber_leased` | Line | 2 | Leased segments only |
| `fiber_lift` | Line | 6 | Lift fiber segments |
| `fiber_defunct` | Line | 1 | Defunct 6-strand MM corridor |
| `network_summary` | Table | 21 | Summary statistics |

Open in: **ArcGIS Pro**, **QGIS**, **CARTO**, or any GDAL-compatible tool.

---

## Setup

```bash
git clone https://github.com/jcvignatti/stowe-fiber-gis.git
cd stowe-fiber-gis
pip install -r requirements.txt
```

### Run the full pipeline

```bash
python scripts/stage1_nodes_edges.py          # Build nodes + edges
python scripts/stage2b_estimated_elevation.py # 3D distances (estimated elev)
python scripts/stage3_carto_export.py         # CARTO export
python scripts/build_geodatabase.py           # Build GeoPackage
```

### LiDAR-validated elevation (run locally, requires internet access to Vermont S3)

```bash
python scripts/stage2a_dem.py
```

Requires access to:
```
https://s3.us-east-2.amazonaws.com/vtopendata-prd/_Other/Projects/2023_Lidar/PreliminaryData/Statewide_2023_35cm_DEMHF.tif
```

See `data/dem/README_dem.md` for full instructions.

---

## Data Notes

- **Elevation source:** Estimated from Stowe terrain knowledge pending QL1 LiDAR validation. Run `stage2a_dem.py` locally for DEM-corrected values. Expected correction: ±5–10% on steep segments.
- **F.A.A.T Building:** Identity unconfirmed. Coordinates approximate. High probability this is a snowmaking distribution hub — 60-strand run from Spruce Camp supports this. Verify with Mountain Ops / Snowmaking team.
- **Toll Road Shack:** Standalone vehicle toll facility. No confirmed fiber connection. Flagged `unverified`.
- **Leased segments:** Two segments (SML → Admin, 6 SM; Admin → Warehouse, 2 SM) are not Vail-owned. See `docs/recommendations.md` for cost analysis.
- **Defunct segment:** 6-strand multi-mode run on MOC → Mansfield Lodge corridor. Still physically in place but not in service.

---

## CARTO Visualization

Upload `data/processed/carto_nodes.geojson` and `data/processed/carto_edges.geojson` to CARTO.  
Follow the full style guide: `docs/CARTO_STYLE_GUIDE.md`

Default center: `44.527, -72.789` | Default zoom: `13`

---

## Related Projects

- Uniform Manager Power BI migration: `github.com/jcvignatti/Uniform-ST-VR`
