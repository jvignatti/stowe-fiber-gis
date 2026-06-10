import os
import pandas as pd
import geopandas as gpd
import numpy as np
import json
from shapely.geometry import Point, LineString
from pyproj import Transformer

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR       = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR   = os.path.join(BASE_DIR, "reports")
DOCS_DIR      = os.path.join(BASE_DIR, "docs")

# ─────────────────────────────────────────────────────────────
# LOAD FROM STAGE 2B OUTPUTS
# ─────────────────────────────────────────────────────────────
nodes_df = pd.read_csv(os.path.join(RAW_DIR, "nodes_3d.csv"))
edges_df = pd.read_csv(os.path.join(RAW_DIR, "edges_3d.csv"))

node_lookup = {
    r["name"]: {"lon": r["lon"], "lat": r["lat"], "elev_m": r["elev_m"]}
    for _, r in nodes_df.iterrows()
}

# ─────────────────────────────────────────────────────────────
# ENRICH NODES FOR CARTO
# ─────────────────────────────────────────────────────────────
def node_color(status):
    return {
        "active":           "#2ECC71",   # green
        "inferred_active":  "#F39C12",   # amber
        "unverified":       "#E74C3C",   # red
        "defunct":          "#95A5A6",   # grey
    }.get(status, "#BDC3C7")

def node_icon(zone):
    return {
        "Mountain Base":    "mountain",
        "Mid Mountain":     "ski",
        "Upper Mountain":   "peak",
        "Base Village":     "building",
    }.get(zone, "dot")

nodes_df["marker_color"]    = nodes_df["status"].apply(node_color)
nodes_df["marker_icon"]     = nodes_df["zone"].apply(node_icon)
nodes_df["elev_ft"]         = (nodes_df["elev_m"] * 3.28084).round(0)
nodes_df["popup_html"]      = nodes_df.apply(lambda r: (
    f"<b>{r['name']}</b><br>"
    f"Zone: {r['zone']}<br>"
    f"Status: {r['status']}<br>"
    f"Elevation: {r['elev_ft']:.0f} ft ({r['elev_m']:.0f} m)<br>"
    f"Elev source: {r['elev_source']}"
), axis=1)

# ─────────────────────────────────────────────────────────────
# ENRICH EDGES FOR CARTO
# ─────────────────────────────────────────────────────────────
def edge_color(row):
    if row["defunct"]:          return "#95A5A6"   # grey  - defunct
    if row["leased"]:           return "#9B59B6"   # purple - leased
    if row["segment_type"] == "lift": return "#E67E22"  # orange - lift
    if row["fiber_type"] == "MM":    return "#3498DB"   # blue - multimode
    return "#2ECC71"                                # green - SM buried

def edge_width(strand_count):
    if strand_count >= 48:  return 5
    if strand_count >= 24:  return 4
    if strand_count >= 12:  return 3
    if strand_count >= 6:   return 2
    return 1.5

def edge_dash(row):
    if row["defunct"]:           return "4,4"
    if row["leased"]:            return "8,4"
    if row["segment_type"] == "lift": return "2,2"
    return "none"

edges_df["line_color"]   = edges_df.apply(edge_color, axis=1)
edges_df["line_width"]   = edges_df["strand_count"].apply(edge_width)
edges_df["line_dash"]    = edges_df.apply(edge_dash, axis=1)
edges_df["length_3d_ft"] = (edges_df["length_3d_m"] * 3.28084).round(0)
edges_df["length_3d_mi"] = (edges_df["length_3d_m"] / 1609.344).round(3)
edges_df["elev_delta_ft"]= (edges_df["elev_delta_m"] * 3.28084).round(0)

def fiber_label(ft):
    return {"SM": "Single-Mode", "MM": "Multi-Mode", "LF": "Lift Fiber"}.get(ft, ft)

edges_df["fiber_label"] = edges_df["fiber_type"].apply(fiber_label)

edges_df["popup_html"] = edges_df.apply(lambda r: (
    f"<b>{r['from_node']} -> {r['to_node']}</b><br>"
    f"Type: {r['fiber_label']}"
    + (f" ({r['strand_count']} strand)" if r['strand_count'] > 0 else "") + "<br>"
    f"Segment: {r['segment_type'].title()}<br>"
    f"Length 2D: {r['length_2d_ft']:,.0f} ft<br>"
    f"Length 3D: {r['length_3d_ft']:,.0f} ft<br>"
    f"Elev delta: {r['elev_delta_ft']:+,.0f} ft<br>"
    + ("DEFUNCT<br>" if r["defunct"] else "")
    + ("LEASED<br>"  if r["leased"]  else "")
    + (f"Notes: {r['notes']}" if r["notes"] else "")
), axis=1)

# ─────────────────────────────────────────────────────────────
# BUILD GEODATAFRAMES
# ─────────────────────────────────────────────────────────────
nodes_df["geometry"] = nodes_df.apply(
    lambda r: Point(r["lon"], r["lat"]), axis=1)
nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry="geometry", crs="EPSG:4326")

def make_line(row):
    a = node_lookup.get(row["from_node"])
    b = node_lookup.get(row["to_node"])
    if a and b:
        return LineString([(a["lon"], a["lat"]), (b["lon"], b["lat"])])

edges_df["geometry"] = edges_df.apply(make_line, axis=1)
edges_gdf = gpd.GeoDataFrame(edges_df, geometry="geometry", crs="EPSG:4326")

# ─────────────────────────────────────────────────────────────
# SAVE CARTO GEOJSON
# ─────────────────────────────────────────────────────────────
nodes_gdf.to_file(os.path.join(PROCESSED_DIR, "carto_nodes.geojson"), driver="GeoJSON")
edges_gdf.to_file(os.path.join(PROCESSED_DIR, "carto_edges.geojson"), driver="GeoJSON")

# Also save flat CSV for CARTO table upload (nodes)
nodes_df.drop("geometry", axis=1).to_csv(os.path.join(PROCESSED_DIR, "carto_nodes.csv"), index=False)
edges_df.drop("geometry", axis=1).to_csv(os.path.join(PROCESSED_DIR, "carto_edges.csv"), index=False)

# ─────────────────────────────────────────────────────────────
# DASHBOARD SUMMARY JSON
# ─────────────────────────────────────────────────────────────
active_edges   = edges_df[~edges_df["defunct"]]
owned_edges    = active_edges[~active_edges["leased"]]
leased_edges   = active_edges[active_edges["leased"]]
lift_edges     = active_edges[active_edges["segment_type"] == "lift"]
buried_edges   = active_edges[active_edges["segment_type"] == "buried"]
defunct_edges  = edges_df[edges_df["defunct"]]

dashboard = {
    "network_summary": {
        "total_nodes":          int(len(nodes_df)),
        "active_nodes":         int(len(nodes_df[nodes_df["status"]=="active"])),
        "inferred_nodes":       int(len(nodes_df[nodes_df["status"]=="inferred_active"])),
        "unverified_nodes":     int(len(nodes_df[nodes_df["status"]=="unverified"])),
        "total_segments":       int(len(edges_df)),
    },
    "network_length": {
        "total_3d_m":           round(active_edges["length_3d_m"].sum(), 1),
        "total_3d_ft":          round(active_edges["length_3d_m"].sum() * 3.28084, 0),
        "total_3d_mi":          round(active_edges["length_3d_m"].sum() / 1609.344, 2),
        "owned_3d_ft":          round(owned_edges["length_3d_m"].sum() * 3.28084, 0),
        "leased_3d_ft":         round(leased_edges["length_3d_m"].sum() * 3.28084, 0),
        "lift_fiber_3d_ft":     round(lift_edges["length_3d_m"].sum() * 3.28084, 0),
        "buried_3d_ft":         round(buried_edges["length_3d_m"].sum() * 3.28084, 0),
        "defunct_3d_ft":        round(defunct_edges["length_3d_m"].sum() * 3.28084, 0),
        "elevation_correction_pct": round(
            (active_edges["length_3d_m"].sum() - active_edges["length_2d_m"].sum())
            / active_edges["length_2d_m"].sum() * 100, 1),
    },
    "fiber_breakdown": {
        "single_mode_segments": int(len(active_edges[active_edges["fiber_type"]=="SM"])),
        "multi_mode_segments":  int(len(active_edges[active_edges["fiber_type"]=="MM"])),
        "lift_fiber_segments":  int(len(active_edges[active_edges["fiber_type"]=="LF"])),
        "max_strand_count":     int(active_edges["strand_count"].max()),
        "segments_60_strand":   int(len(active_edges[active_edges["strand_count"]==60])),
        "segments_48_strand":   int(len(active_edges[active_edges["strand_count"]==48])),
    },
    "flags": {
        "defunct_segments":     int(len(defunct_edges)),
        "leased_segments":      int(len(leased_edges)),
        "unverified_nodes":     int(len(nodes_df[nodes_df["status"]=="unverified"])),
        "lift_segments_no_strand_count": int(len(lift_edges[lift_edges["strand_count"]==0])),
    },
    "elevation": {
        "elev_source":          "estimated (QL1 LiDAR pending local run)",
        "min_node_elev_ft":     round(nodes_df["elev_ft"].min(), 0),
        "max_node_elev_ft":     round(nodes_df["elev_ft"].max(), 0),
        "vertical_range_ft":    round(nodes_df["elev_ft"].max() - nodes_df["elev_ft"].min(), 0),
    }
}

with open(os.path.join(REPORTS_DIR, "dashboard_summary.json"), "w") as f:
    json.dump(dashboard, f, indent=2)

# ─────────────────────────────────────────────────────────────
# CARTO STYLE GUIDE (as a ready-to-use reference)
# ─────────────────────────────────────────────────────────────
style_guide = """
# CARTO Map Style Guide - Stowe Fiber Network
# ============================================

## LAYER 1: fiber_edges (carto_edges.geojson)
Upload as: carto_edges.geojson
Geometry: LineString

### Line color by segment type:
  #2ECC71  ->Single-Mode buried (active, owned)
  #3498DB  ->Multi-Mode buried
  #E67E22  ->Lift fiber
  #9B59B6  ->Leased
  #95A5A6  ->Defunct

### Line width by strand count:
  5px  ->48+ strands
  4px  ->24-47 strands
  3px  ->12-23 strands
  2px  ->6-11 strands
  1.5px→  <6 strands

### Line dash pattern:
  solid  ->active owned buried
  8,4    ->leased
  2,2    ->lift fiber
  4,4    ->defunct

### Pop-up fields to enable:
  from_node, to_node, fiber_label, strand_count,
  segment_type, length_2d_ft, length_3d_ft,
  elev_delta_ft, leased, defunct, notes

---

## LAYER 2: fiber_nodes (carto_nodes.geojson)
Upload as: carto_nodes.geojson
Geometry: Point

### Marker color by status:
  #2ECC71  ->active
  #F39C12  ->inferred_active
  #E74C3C  ->unverified
  #95A5A6  ->defunct

### Marker size:
  12px  ->hub nodes (MOC, Spruce Camp, Admin)
  8px   ->all others

### Pop-up fields to enable:
  name, zone, status, elev_ft, elev_m, elev_source

---

## DASHBOARD WIDGETS (CARTO Builder)

Widget 1: Category — segment_type (buried / lift / leased)
Widget 2: Category — fiber_type (SM / MM / LF)
Widget 3: Histogram — length_3d_ft
Widget 4: Formula — SUM(length_3d_ft) / 5280  -> Total miles
Widget 5: Category — status (nodes layer)
Widget 6: Formula — COUNT where defunct=true

## RECOMMENDED BASEMAP
  CARTO Dark Matter  or  Positron (light)
  Both show mountain terrain well at zoom 12-14

## SUGGESTED ZOOM
  Default center: 44.527, -72.789
  Default zoom:   13
"""

with open(os.path.join(DOCS_DIR, "CARTO_STYLE_GUIDE.md"), "w", encoding="utf-8") as f:
    f.write(style_guide)

# ─────────────────────────────────────────────────────────────
# PRINT SUMMARY
# ─────────────────────────────────────────────────────────────
d = dashboard
print("=" * 58)
print("  STAGE 3 — CARTO EXPORT SUMMARY")
print("=" * 58)
print(f"\n  NODES: {d['network_summary']['total_nodes']} total")
print(f"    Active      : {d['network_summary']['active_nodes']}")
print(f"    Inferred    : {d['network_summary']['inferred_nodes']}")
print(f"    Unverified  : {d['network_summary']['unverified_nodes']}")

print(f"\n  NETWORK LENGTH (3D with elevation):")
print(f"    Total       : {d['network_length']['total_3d_ft']:,.0f} ft  |  {d['network_length']['total_3d_mi']} miles")
print(f"    Owned       : {d['network_length']['owned_3d_ft']:,.0f} ft")
print(f"    Leased      : {d['network_length']['leased_3d_ft']:,.0f} ft")
print(f"    Lift fiber  : {d['network_length']['lift_fiber_3d_ft']:,.0f} ft")
print(f"    Buried      : {d['network_length']['buried_3d_ft']:,.0f} ft")
print(f"    Defunct     : {d['network_length']['defunct_3d_ft']:,.0f} ft  (excluded)")
print(f"    Elev corr.  : +{d['network_length']['elevation_correction_pct']}% over 2D")

print(f"\n  ELEVATION RANGE:")
print(f"    Low  : {d['elevation']['min_node_elev_ft']:,.0f} ft")
print(f"    High : {d['elevation']['max_node_elev_ft']:,.0f} ft")
print(f"    Range: {d['elevation']['vertical_range_ft']:,.0f} ft vertical")

print(f"\n  FLAGS:")
print(f"    Defunct segments  : {d['flags']['defunct_segments']}")
print(f"    Leased segments   : {d['flags']['leased_segments']}")
print(f"    Unverified nodes  : {d['flags']['unverified_nodes']}")

print(f"\nFiles ready for CARTO upload:")
print(f"    carto_nodes.geojson")
print(f"    carto_edges.geojson")
print(f"    carto_nodes.csv")
print(f"    carto_edges.csv")
print(f"    dashboard_summary.json")
print(f"    CARTO_STYLE_GUIDE.md")
