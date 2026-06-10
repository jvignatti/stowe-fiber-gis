# Stowe Mountain Resort — Fiber Network GIS Analysis

**Author:** JC Vignatti, Mountain Operations  
**Department:** Mountain Operations / IT Infrastructure Support  
**Resort:** Stowe Mountain Resort, Vail Resorts  
**Completed:** 2026  
**Repository:** github.com/jcvignatti/stowe-fiber-gis

---

## 1. Context

This project was initiated as a structured knowledge transfer from Mountain Operations to IT. The fiber network exists, is operational, and is largely undocumented in any spatial format. The goal was to take what exists in a single relationship diagram, a list of coordinates, and institutional knowledge, and produce a dataset that IT can maintain, query, and build on.

The work was done collaboratively using Python, open-source GIS libraries, and CARTO for visualization. No ArcGIS Pro license was required for the analysis — the pipeline runs entirely on open standards.

---

## 2. Source Data

| Input | Format | Source |
|-------|--------|--------|
| Node coordinates | Lat/long list | Field knowledge — JC Vignatti |
| Network topology | PNG diagram | Existing IT documentation |
| Fiber type/strand counts | Annotated on diagram | Existing IT documentation |
| Elevation | Estimated (see §4.2) | Stowe terrain knowledge |
| Vermont QL1 LiDAR DEM | GeoTIFF (35cm) | Vermont Open Geodata — S3 |

The topology diagram was the authoritative source for connections, fiber types, and strand counts. Where the diagram and coordinate list conflicted or had gaps, conflicts are documented in §6.

---

## 3. Methodology

### 3.1 Network Construction

All 47 nodes were defined as WGS 84 point features (EPSG:4326) from the provided coordinate list. Edges were defined as straight-line segments between node pairs derived from the topology diagram, attributed with:

- Fiber type (SM / MM / LF — lift fiber)
- Strand count
- Segment type (buried / lift / leased)
- Leased flag
- Defunct flag
- Notes

The final dataset contains **40 edges** across all status types.

### 3.2 Distance Calculation — 2D Baseline

All segments were projected to UTM Zone 18N (EPSG:32618) for metric distance calculation. This gives geodesic accuracy appropriate for the scale of the network (~12 km maximum extent).

2D distances treat the network as flat — no elevation. These are used as the baseline for comparison.

### 3.3 Distance Calculation — 3D with Elevation

Stowe spans **2,444 ft of vertical relief** (1,165 ft at Nordic Center to 3,609 ft at Ski Patrol Spruce Side). Ignoring elevation systematically underestimates cable length, particularly on steep segments.

The 3D distance formula applied per segment:

```
d3 = sqrt(dx² + dy² + dz²)
```

Where dx, dy are UTM easting/northing differences and dz is elevation difference in meters.

**Elevation data source:** Estimated from Stowe terrain knowledge pending local validation against the Vermont QL1 LiDAR DEM. A complete local-run script (`scripts/stage2a_dem.py`) is included that:

1. Opens the Vermont 35cm LiDAR DEM via S3 URL (windowed read — only the network bounding box)
2. Densifies each line segment at 10m intervals
3. Samples DEM elevation at every vertex
4. Calculates cumulative 3D length along the densified path

This is the correct method per ArcGIS Pro's Add Z Information tool, replicated in open-source Python. Expected improvement over point-to-point 3D: 3–8% on steep segments due to terrain undulation.

**Overall elevation correction:** +3.7% above 2D flat distances across the active network.

High-correction segments to note:

| Segment | 2D (ft) | 3D (ft) | Correction |
|---------|---------|---------|------------|
| Bldg N → Stowe Mountain Lodge | 101 | 153 | +51.5% |
| Spruce Camp → Bldg M | 244 | 313 | +28.6% |
| F.A.A.T → Sunny Quad | 285 | 346 | +21.6% |
| Spruce Camp → F.A.A.T | 457 | 544 | +19.1% |
| MOC → Spruce Camp (direct) | 1,464 | 1,597 | +9.1% |

### 3.4 Lift Fiber Treatment

Lift fiber segments follow cable geometry — towers, sag, and angle — not ground surface. The DEM approach slightly overestimates lift fiber length (ground surface ≠ cable path). These segments are flagged `segment_type = lift` and should be treated as estimates pending tower coordinate data from lift maintenance.

Typical lift cable correction factor over slope distance: +8–12%.

### 3.5 Output Pipeline

```
stage1_nodes_edges.py         →  base node/edge GeoJSON + CSV
stage2b_estimated_elevation.py →  3D distances (estimated elev)
stage2a_dem.py                 →  3D distances (LiDAR validated, run locally)
stage3_carto_export.py         →  CARTO-ready GeoJSON with styling metadata
build_geodatabase.py           →  stowe_fiber_network.gpkg (7 layers)
```

All outputs use EPSG:4326. The GeoPackage is the single-file deliverable for ArcGIS Pro or QGIS.

---

## 4. Network Inventory

### 4.1 Summary

| Metric | Value |
|--------|-------|
| Total nodes | 47 |
| Active nodes | 35 |
| Inferred active (lift returns) | 9 |
| Unverified | 3 |
| Total segments | 40 |
| **Active network (3D)** | **42,351 ft / 8.02 miles** |
| Owned fiber | 32,266 ft / 6.11 miles |
| Leased fiber | 10,085 ft / 1.91 miles |
| Lift fiber (of owned) | 16,045 ft / 3.04 miles |
| Buried owned | 16,221 ft / 3.07 miles |
| **Defunct (excluded)** | **8,979 ft / 1.70 miles** |
| Vertical range | 1,165 ft – 3,609 ft (2,444 ft) |
| Elevation correction over 2D | +3.7% |

### 4.2 Primary Hubs

| Hub | Zone | Elevation | Role |
|-----|------|-----------|------|
| MOC | Mountain Base | ~1,296 ft | Primary — mountain side |
| Spruce Camp | Mid Mountain | ~1,936 ft | Primary — Spruce Peak side |
| Admin | Base Village | ~1,280 ft | Primary — village side |

### 4.3 Fiber Breakdown

| Type | Segments | Notes |
|------|----------|-------|
| Single-Mode (SM) | 30 | Standard for all active owned runs |
| Multi-Mode (MM) | 4 | MOC→Mansfield (×2, both active), SML→First Chair, Admin→Inn |
| Lift Fiber (LF) | 6 | Aerial, follows lift cable geometry |

### 4.4 Leased Segments

| Segment | Strands | Length (3D) | Risk |
|---------|---------|-------------|------|
| Stowe Mountain Lodge → Admin | 6 SM | 8,207 ft | High — sole path to Admin hub |
| Admin → Warehouse | 2 SM | 1,878 ft | Medium — affects base ops cluster |

### 4.5 Defunct Segment

| Segment | Type | Length | Notes |
|---------|------|--------|-------|
| MOC → The Inn | Unknown | 8,979 ft / 1.70 mi | Original backbone run. Out of service — type and strand count unconfirmed. Likely predates current Admin hub architecture. |

---

## 5. Decisions & Assumptions Log

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Deduplication deferred | Raw data inspected first; inconsistencies surfaced before cleaning decisions made |
| D2 | Lift return stations flagged `inferred_active` | Every lift has two terminals; returns are logical extensions of confirmed drive stations |
| D3 | F.A.A.T Building coordinates approximated | Identity unconfirmed; positioned near Spruce Camp cluster based on topology diagram placement |
| D4 | Toll Road Shack marked `unverified` | Vehicle toll facility — no confirmed fiber connection; separate from lift system |
| D5 | Building Maintenance XC marked `unverified` | Missing from topology diagram; may be historical only |
| D6 | Elevation estimated from terrain knowledge | Vermont S3 bucket inaccessible from analysis environment; `stage2a_dem.py` provided for local LiDAR validation |
| D7 | Lift fiber strand counts logged as 0 | Not visible in source diagram; requires field confirmation |
| D8 | MOC→Mansfield MM corrected to active | Initially flagged defunct based on diagram annotation misread; JC confirmed both runs are operational |
| D9 | MOC→The Inn added as defunct | JC confirmed 1.70-mile run exists but is out of service; fiber type and strand count unknown |
| D10 | GeoPackage format chosen over ESRI FileGDB | Open standard; no license required; native support in ArcGIS Pro, QGIS, CARTO, and all GDAL tools |
| D11 | Leased segment Admin→Warehouse flagged separately | Cost and risk profile differs from owned infrastructure; requires distinct treatment in reporting |

---

## 6. Open Items

These require field verification or IT input — not assumptions that can be resolved from existing documentation.

| Item | Priority | Action needed |
|------|----------|---------------|
| F.A.A.T Building identity | High | Confirm with Mountain Ops / Snowmaking team |
| MOC→The Inn defunct run | High | Confirm fiber type, strand count, reason for decommission |
| Lift fiber strand counts | Medium | Field check or ask lift maintenance |
| Toll Road Shack connectivity | Medium | Confirm whether fiber exists |
| Building Maintenance XC | Low | Confirm active or historical only |
| LiDAR elevation validation | Low | Run `stage2a_dem.py` locally when S3 access available |
| Leased segment contract terms | High | Pull from Vail procurement — expiry, rate escalators, SLA |

---

## 7. Recommendations

Three findings worth IT's attention. In order of urgency.

---

**The leased SML→Admin run is the highest-risk segment in the network.**  
Admin is the sole hub for the entire base village. Its only upstream path is leased — meaning Vail cannot self-dispatch for repairs, and restoration time depends entirely on the vendor. Pull the contract. If there's no restoration SLA, negotiate one now. If the lease is within two years of renewal, start the capital conversation in parallel.

---

**The MOC→Spruce Camp corridor has no physical redundancy.**  
There are two paths — direct buried and via Over Easy lift fiber — but the lift path is aerial, weather-dependent, and unavailable when the lift is down. A single backhoe on the wrong road takes out Spruce Camp hub, which means snowmaking control, upper mountain lift communications, and the Bldg M/N/SML cluster all go dark simultaneously. During Presidents' Week that exposure is north of $1M/day. A second buried run on a separate route is the fix — it doesn't need to be 60 strands, just physically independent.

---

**1.70 miles of unknown defunct fiber runs between MOC and The Inn.**  
It's in the ground, it's not in any current topology, and nobody knows the condition. That's not urgent but it needs to land in the asset registry with a status — either confirmed decommissioned and documented, or assessed for reuse. Leaving it undocumented is the only wrong answer.

---

*Pre-stage emergency splice kits at MOC and Spruce Camp. Kit cost ~$3–5k. Restoration time drops from 24+ hours to 2–4 hours on a buried cut. This is the cheapest resilience improvement available.*

---

## 8. CARTO Visualization

Upload `data/processed/carto_nodes.geojson` and `data/processed/carto_edges.geojson`.  
Configuration guide: `docs/CARTO_STYLE_GUIDE.md`  
Default center: `44.527, -72.789` | Zoom: `13`

Line weight encodes strand count. Color encodes segment type. Pop-up fields are pre-configured in the GeoJSON attributes.

---

## 9. Files

```
stowe-fiber-gis/
├── data/
│   ├── raw/                         Source CSVs — nodes, edges, 3D variants
│   ├── processed/
│   │   ├── stowe_fiber_network.gpkg  GeoPackage — 7 layers, open in ArcGIS Pro / QGIS
│   │   ├── carto_nodes.geojson       CARTO upload — points
│   │   ├── carto_edges.geojson       CARTO upload — lines
│   │   ├── nodes_3d.geojson
│   │   └── edges_3d.geojson
│   └── dem/                         LiDAR instructions
├── scripts/
│   ├── stage1_nodes_edges.py
│   ├── stage2a_dem.py               Run locally for LiDAR-validated elevations
│   ├── stage2b_estimated_elevation.py
│   ├── stage3_carto_export.py
│   └── build_geodatabase.py
├── docs/
│   ├── MASTER.md                    This document
│   ├── CARTO_STYLE_GUIDE.md
│   └── network_topology.md
├── reports/
│   └── dashboard_summary.json
├── requirements.txt
└── .gitignore
```

---

## 10. Running the Pipeline

```bash
git clone https://github.com/jcvignatti/stowe-fiber-gis.git
cd stowe-fiber-gis
pip install -r requirements.txt

python scripts/stage1_nodes_edges.py
python scripts/stage2b_estimated_elevation.py
python scripts/stage3_carto_export.py
python scripts/build_geodatabase.py

# For LiDAR-validated elevations (run locally with S3 access):
python scripts/stage2a_dem.py
```
