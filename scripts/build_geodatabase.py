"""
build_geodatabase.py
====================
Builds the Stowe Fiber Network GeoPackage (.gpkg)
GeoPackage is the open-source equivalent of an ESRI File Geodatabase.
Supported by: ArcGIS Pro, QGIS, CARTO, PostGIS, and all GDAL tools.

Layers created:
  - fiber_nodes       : Point layer -all 47 network nodes
  - fiber_edges       : Line layer  -all 39 network segments
  - fiber_hubs        : Point layer -MOC, Spruce Camp, Admin (major hubs only)
  - fiber_leased      : Line layer  -leased segments only
  - fiber_lift        : Line layer  -lift fiber segments only
  - fiber_defunct     : Line layer  -defunct segments
  - network_summary   : Non-spatial attribute table (summary stats)
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
import json, os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR     = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_GPKG = os.path.join(BASE_DIR, "data", "processed", "stowe_fiber_network.gpkg")

# ─────────────────────────────────────────────────────────────
# LOAD BASE DATA
# ─────────────────────────────────────────────────────────────
nodes_df = pd.read_csv(f"{RAW_DIR}/nodes_3d.csv")
edges_df = pd.read_csv(f"{RAW_DIR}/edges_3d.csv")

node_lookup = {
    r["name"]: {"lon": r["lon"], "lat": r["lat"], "elev_m": r["elev_m"]}
    for _, r in nodes_df.iterrows()
}

# ─────────────────────────────────────────────────────────────
# BUILD GEOMETRIES
# ─────────────────────────────────────────────────────────────
nodes_df["geometry"] = nodes_df.apply(
    lambda r: Point(r["lon"], r["lat"]), axis=1)

def make_line(row):
    a = node_lookup.get(row["from_node"])
    b = node_lookup.get(row["to_node"])
    if a and b:
        return LineString([(a["lon"], a["lat"]), (b["lon"], b["lat"])])
    return None

edges_df["geometry"] = edges_df.apply(make_line, axis=1)

# ─────────────────────────────────────────────────────────────
# ENRICH WITH DISPLAY FIELDS
# ─────────────────────────────────────────────────────────────
nodes_df["elev_ft"]      = (nodes_df["elev_m"] * 3.28084).round(1)
nodes_df["is_hub"]       = nodes_df["name"].isin(["MOC", "Spruce Camp", "Admin"])
nodes_df["hub_type"]     = nodes_df["name"].map({
    "MOC":          "Primary -Mountain",
    "Spruce Camp":  "Primary -Spruce Side",
    "Admin":        "Primary -Base Village"
}).fillna("")

edges_df["fiber_label"]    = edges_df["fiber_type"].map(
    {"SM": "Single-Mode", "MM": "Multi-Mode", "LF": "Lift Fiber"})
edges_df["length_2d_ft"]   = (edges_df["length_2d_m"] * 3.28084).round(1)
edges_df["length_3d_ft"]   = (edges_df["length_3d_m"] * 3.28084).round(1)
edges_df["length_2d_mi"]   = (edges_df["length_2d_m"] / 1609.344).round(4)
edges_df["length_3d_mi"]   = (edges_df["length_3d_m"] / 1609.344).round(4)
edges_df["elev_delta_ft"]  = (edges_df["elev_delta_m"] * 3.28084).round(1)
edges_df["strand_label"]   = edges_df["strand_count"].apply(
    lambda x: f"{x}-strand" if x > 0 else "unknown")

# ─────────────────────────────────────────────────────────────
# DEFINE LAYER COLUMNS
# ─────────────────────────────────────────────────────────────
NODE_COLS = [
    "name","zone","status","elev_m","elev_ft","elev_source",
    "is_hub","hub_type","lat","lon","geometry"
]
EDGE_COLS = [
    "from_node","to_node","fiber_type","fiber_label","strand_count","strand_label",
    "segment_type","leased","defunct","notes",
    "length_2d_m","length_2d_ft","length_2d_mi",
    "length_3d_m","length_3d_ft","length_3d_mi",
    "elev_delta_m","elev_delta_ft","elev_correction_pct","elev_source",
    "geometry"
]

nodes_gdf = gpd.GeoDataFrame(nodes_df[NODE_COLS], geometry="geometry", crs="EPSG:4326")
edges_gdf = gpd.GeoDataFrame(edges_df[EDGE_COLS], geometry="geometry", crs="EPSG:4326")

# ─────────────────────────────────────────────────────────────
# DERIVED LAYERS
# ─────────────────────────────────────────────────────────────
hubs_gdf   = nodes_gdf[nodes_gdf["is_hub"] == True].copy()
leased_gdf = edges_gdf[edges_gdf["leased"] == True].copy()
lift_gdf   = edges_gdf[edges_gdf["segment_type"] == "lift"].copy()
defunct_gdf= edges_gdf[edges_gdf["defunct"] == True].copy()

# ─────────────────────────────────────────────────────────────
# SUMMARY TABLE (non-spatial -stored as attribute CSV in gpkg)
# ─────────────────────────────────────────────────────────────
active = edges_gdf[edges_gdf["defunct"] == False]
owned  = active[active["leased"] == False]
leased = active[active["leased"] == True]

summary_rows = [
    ("Total nodes",                 len(nodes_gdf),                              "count"),
    ("Active nodes",                len(nodes_gdf[nodes_gdf["status"]=="active"]), "count"),
    ("Inferred active nodes",       len(nodes_gdf[nodes_gdf["status"]=="inferred_active"]), "count"),
    ("Unverified nodes",            len(nodes_gdf[nodes_gdf["status"]=="unverified"]), "count"),
    ("Total segments",              len(edges_gdf),                              "count"),
    ("Total length 3D (ft)",        round(active["length_3d_ft"].sum(), 1),      "feet"),
    ("Total length 3D (miles)",     round(active["length_3d_mi"].sum(), 3),      "miles"),
    ("Owned fiber length (ft)",     round(owned["length_3d_ft"].sum(), 1),       "feet"),
    ("Leased fiber length (ft)",    round(leased["length_3d_ft"].sum(), 1),      "feet"),
    ("Lift fiber length (ft)",      round(lift_gdf["length_3d_ft"].sum(), 1),    "feet"),
    ("Buried fiber length (ft)",    round(active[active["segment_type"]=="buried"]["length_3d_ft"].sum(), 1), "feet"),
    ("Defunct length (ft)",         round(defunct_gdf["length_3d_ft"].sum(), 1), "feet"),
    ("Elevation correction %",      round((active["length_3d_m"].sum() - active["length_2d_m"].sum()) / active["length_2d_m"].sum() * 100, 2), "percent"),
    ("Min elevation (ft)",          round(nodes_gdf["elev_ft"].min(), 0),        "feet"),
    ("Max elevation (ft)",          round(nodes_gdf["elev_ft"].max(), 0),        "feet"),
    ("Vertical range (ft)",         round(nodes_gdf["elev_ft"].max() - nodes_gdf["elev_ft"].min(), 0), "feet"),
    ("Max strand count",            int(active["strand_count"].max()),            "strands"),
    ("Elevation data source",       "estimated (QL1 LiDAR pending)",             "text"),
    ("Coordinate system",           "EPSG:4326 (WGS 84)",                        "text"),
    ("Data compiled",               "2026",                                       "text"),
    ("Resort",                      "Stowe Mountain Resort -Vail Resorts",       "text"),
]
summary_df = pd.DataFrame(summary_rows, columns=["metric","value","unit"])

# ─────────────────────────────────────────────────────────────
# WRITE GEOPACKAGE
# ─────────────────────────────────────────────────────────────
if os.path.exists(OUTPUT_GPKG):
    os.remove(OUTPUT_GPKG)

layers = [
    (nodes_gdf,   "fiber_nodes",   "All network nodes (47)"),
    (edges_gdf,   "fiber_edges",   "All network segments (39)"),
    (hubs_gdf,    "fiber_hubs",    "Primary hub nodes (MOC, Spruce Camp, Admin)"),
    (leased_gdf,  "fiber_leased",  "Leased fiber segments"),
    (lift_gdf,    "fiber_lift",    "Lift fiber segments"),
    (defunct_gdf, "fiber_defunct", "Defunct segments"),
]

for gdf, layer_name, desc in layers:
    gdf.to_file(OUTPUT_GPKG, layer=layer_name, driver="GPKG")
    print(f"  OKLayer '{layer_name}': {len(gdf)} features -{desc}")

# Write summary as non-spatial table via SQLite (GPKG is SQLite under the hood)
import sqlite3
conn = sqlite3.connect(OUTPUT_GPKG)
summary_df.to_sql("network_summary", conn, if_exists="replace", index=False)
conn.close()
print(f"  OKTable 'network_summary': {len(summary_df)} rows")

# -----------------------------------------------------------
# VERIFY GPKG
# -----------------------------------------------------------
size_kb = os.path.getsize(OUTPUT_GPKG) / 1024
print(f"\n  File size: {size_kb:.1f} KB")
print(f"\nGeoPackage complete: stowe_fiber_network.gpkg")
