"""
STAGE 2A — LiDAR DEM 3D Distance Calculator
============================================
Run this LOCALLY with ArcGIS Pro Python env or any Python env 
that has: rasterio, geopandas, shapely, pyproj, numpy, pandas

Vermont QL1 LiDAR DEM (35cm resolution):
https://s3.us-east-2.amazonaws.com/vtopendata-prd/_Other/Projects/2023_Lidar/PreliminaryData/Statewide_2023_35cm_DEMHF.tif

ArcGIS Pro users: run from ArcGIS Pro Python Command Prompt
  pip install rasterio geopandas pyproj

Usage:
  python stage2a_dem.py

Outputs:
  nodes_dem.geojson   - nodes with LiDAR-validated elevations
  edges_dem.geojson   - edges with true 3D lengths
  edges_dem.csv       - tabular results
  network_report.txt  - full summary report
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from pyproj import Transformer
import rasterio
from rasterio.windows import from_bounds
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
DEM_URL     = "https://s3.us-east-2.amazonaws.com/vtopendata-prd/_Other/Projects/2023_Lidar/PreliminaryData/Statewide_2023_35cm_DEMHF.tif"
DENSIFY_M   = 10          # Vertex spacing in meters for DEM sampling
BUFFER_DEG  = 0.02        # Bounding box buffer around network
OUTPUT_DIR  = "./"        # Change to your desired output folder

# ─────────────────────────────────────────────────────────────
# NODES
# ─────────────────────────────────────────────────────────────
nodes_raw = [
    ("Vehicles Maintenance",        44.53397478022453,  -72.78970406216413, "Mountain Base",    "active"),
    ("Snowmaking Control",          44.53291282175362,  -72.79019935725232, "Mountain Base",    "active"),
    ("Midway",                      44.53168034157372,  -72.79030874148611, "Mountain Base",    "active"),
    ("Cliff House",                 44.53760695156738,  -72.81426928408973, "Upper Mountain",   "active"),
    ("Gondola Barn",                44.53117296598019,  -72.78758861126525, "Mountain Base",    "active"),
    ("MOC",                         44.53045706260745,  -72.78702517521394, "Mountain Base",    "active"),
    ("Over Easy Drive",             44.53065375182360,  -72.78743026736026, "Mountain Base",    "active"),
    ("Over Easy Return",            44.53061933757054,  -72.78173001274592, "Mid Mountain",     "active"),
    ("Spruce Camp",                 44.53095040595042,  -72.78145485167710, "Mid Mountain",     "active"),
    ("Demo Center",                 44.52877056172229,  -72.78592450609574, "Mountain Base",    "active"),
    ("Four Runner Quad Drive",      44.52887782683637,  -72.78619393875799, "Mountain Base",    "active"),
    ("Four Runner Quad Return",     44.52394935565263,  -72.80786026300211, "Upper Mountain",   "inferred_active"),
    ("Octagon",                     44.52424278249422,  -72.80751887354039, "Upper Mountain",   "active"),
    ("Ski Patrol (269)",            44.52379475357288,  -72.80818265053907, "Upper Mountain",   "active"),
    ("Lookout Double",              44.52830091154923,  -72.78451356020577, "Mountain Base",    "active"),
    ("Mansfield Lodge",             44.52906754186289,  -72.78429138980584, "Mountain Base",    "active"),
    ("Sunrise Drive",               44.52851954600344,  -72.78323016039246, "Mountain Base",    "active"),
    ("Sunny Quad Drive",            44.53146202580196,  -72.78129132378108, "Mid Mountain",     "active"),
    ("Race Shack",                  44.53146202580196,  -72.78129132378108, "Mid Mountain",     "active"),
    ("Meadows Quad Drive",          44.53169465471388,  -72.78007672306560, "Mid Mountain",     "active"),
    ("Adventure Triple Drive",      44.53104047669733,  -72.77959711049780, "Mid Mountain",     "active"),
    ("Sensation Quad Drive",        44.53589261484200,  -72.77568923363755, "Upper Mountain",   "active"),
    ("Sensation Quad Return",       44.55097682958558,  -72.78121081469202, "Upper Mountain",   "inferred_active"),
    ("Ski Patrol Spruce Side",      44.55140830106051,  -72.78123421444815, "Upper Mountain",   "active"),
    ("Turf Building",               44.53560025354428,  -72.77595118335974, "Mid Mountain",     "active"),
    ("Bldg M",                      44.53044232708503,  -72.78084811817001, "Mid Mountain",     "active"),
    ("Bldg N",                      44.52983679413696,  -72.78087623427068, "Mid Mountain",     "active"),
    ("Adventure Center",            44.53067360086118,  -72.77995143399957, "Mid Mountain",     "active"),
    ("Stowe Mountain Lodge",        44.53008098184256,  -72.78105857921837, "Mid Mountain",     "active"),
    ("First Chair",                 44.53024775750400,  -72.78078325489172, "Mid Mountain",     "active"),
    ("Admin",                       44.51051810230879,  -72.76552349656498, "Base Village",     "active"),
    ("The Inn",                     44.51112282588134,  -72.76569787909460, "Base Village",     "active"),
    ("Marketing",                   44.51094463299796,  -72.76648460883614, "Base Village",     "active"),
    ("THCC",                        44.51034183585563,  -72.76668958805115, "Base Village",     "active"),
    ("Warehouse",                   44.50631448179338,  -72.76137472662325, "Base Village",     "active"),
    ("Nordic Center",               44.50543876655190,  -72.76256979955778, "Base Village",     "active"),
    ("FarmHouse",                   44.50605926131790,  -72.76097089707389, "Base Village",     "active"),
    ("Toll Road Shack",             44.51070875298394,  -72.76668338589920, "Base Village",     "unverified"),
    ("TollHouse Double Drive",      44.51079107926899,  -72.76746916540010, "Base Village",     "inferred_active"),
    ("TollHouse Double Return",     44.51904760482018,  -72.78883640755843, "Mountain Base",    "inferred_active"),
    ("Sunrise Return",              44.52055090164348,  -72.79564819987432, "Mountain Base",    "inferred_active"),
    ("Lookout Return",              44.52301019092231,  -72.80209924457878, "Upper Mountain",   "inferred_active"),
    ("Sunny Quad Return",           44.54143198244539,  -72.78284681685732, "Upper Mountain",   "inferred_active"),
    ("Meadows Quad Return",         44.53626281034168,  -72.78067286470414, "Mid Mountain",     "inferred_active"),
    ("Adventure Triple Return",     44.53205987974514,  -72.77621440117946, "Mid Mountain",     "inferred_active"),
    ("Building Maintenance XC",     44.50460989564515,  -72.76287664312079, "Base Village",     "unverified"),
    ("F.A.A.T Building",            44.53200000000000,  -72.78050000000000, "Mid Mountain",     "unverified"),
]

edges_raw = [
    # from, to, fiber_type, strand_count, leased, defunct, segment_type, notes
    ("Gondola Barn","Midway","SM",12,False,False,"buried",""),
    ("Midway","Snowmaking Control","SM",12,False,False,"buried",""),
    ("Snowmaking Control","Vehicles Maintenance","SM",12,False,False,"buried",""),
    ("Gondola Barn","MOC","SM",48,False,False,"buried","Primary backbone"),
    ("Gondola Barn","MOC","SM",12,False,False,"buried","Secondary run"),
    ("Gondola Barn","Cliff House","LF",0,False,False,"lift","Lift fiber - gondola"),
    ("MOC","Demo Center","SM",24,False,False,"buried",""),
    ("Demo Center","Four Runner Quad Drive","SM",12,False,False,"buried",""),
    ("Four Runner Quad Drive","Octagon","LF",0,False,False,"lift","Lift fiber"),
    ("Octagon","Ski Patrol (269)","LF",0,False,False,"lift","Lift fiber"),
    ("Demo Center","Lookout Double","SM",12,False,False,"buried",""),
    ("MOC","Mansfield Lodge","SM",12,False,False,"buried",""),
    ("MOC","Mansfield Lodge","MM",12,False,False,"buried",""),
    ("MOC","Over Easy Drive","LF",12,False,False,"lift","Lift fiber + 12 SM"),
    ("Over Easy Drive","Over Easy Return","LF",0,False,False,"lift","Lift fiber"),
    ("Over Easy Return","Spruce Camp","SM",12,False,False,"buried",""),
    ("MOC","Spruce Camp","SM",12,False,False,"buried","Direct run"),
    ("MOC","The Inn","SM",6,False,True,"buried","Defunct — original backbone run. Type/strand unconfirmed."),
    ("Mansfield Lodge","Sunrise Drive","SM",0,False,False,"buried","Strand count unknown"),
    ("Spruce Camp","F.A.A.T Building","SM",12,False,False,"buried","Likely snowmaking distribution hub - identity unconfirmed"),
    ("Spruce Camp","Sunny Quad Drive","SM",60,False,False,"buried","Largest strand run on Spruce side"),
    ("Sunny Quad Drive","Race Shack","SM",12,False,False,"buried",""),
    ("Sunny Quad Drive","Meadows Quad Drive","SM",12,False,False,"buried",""),
    ("Sunny Quad Drive","Adventure Triple Drive","SM",12,False,False,"buried",""),
    ("Sunny Quad Drive","Sensation Quad Drive","SM",12,False,False,"buried",""),
    ("Sensation Quad Drive","Turf Building","SM",0,False,False,"buried","Strand count unknown"),
    ("Sensation Quad Drive","Ski Patrol Spruce Side","LF",0,False,False,"lift","Lift fiber"),
    ("Spruce Camp","Bldg M (Food Trailer)","SM",12,False,False,"buried","AKA Food Trailer (Stowe Bites)"),
    ("Spruce Camp","Bldg N (Stowe Logo Store)","SM",12,False,False,"buried","AKA Stowe Logo Store"),
    ("Spruce Camp","Adventure Center","SM",24,False,False,"buried",""),
    ("Spruce Camp","Stowe Mountain Lodge","SM",0,False,False,"buried","Strand count unknown"),
    ("Stowe Mountain Lodge","First Chair","MM",6,False,False,"buried",""),
    ("Stowe Mountain Lodge","Admin","SM",6,True,False,"leased","6 strand SM leased"),
    ("Stowe Mountain Lodge","Adventure Center","SM",24,False,False,"buried",""),
    ("Admin","The Inn","SM",12,False,False,"buried",""),
    ("Admin","The Inn","MM",12,False,False,"buried",""),
    ("The Inn","Marketing","SM",12,False,False,"buried",""),
    ("Marketing","THCC","SM",12,False,False,"buried",""),
    ("Admin","Warehouse","SM",2,True,False,"leased","2 strand SM leased"),
    ("Warehouse","FarmHouse","SM",12,False,False,"buried",""),
    ("Warehouse","Nordic Center","SM",12,False,False,"buried",""),
]

# ─────────────────────────────────────────────────────────────
# STEP 1: Load DEM and sample elevations at all nodes
# ─────────────────────────────────────────────────────────────
print("Loading Vermont QL1 LiDAR DEM...")
print(f"Source: {DEM_URL}\n")

nodes_df = pd.DataFrame(nodes_raw, columns=["name","lat","lon","zone","status"])

lats = nodes_df["lat"].values
lons = nodes_df["lon"].values
bbox_minlon = lons.min() - BUFFER_DEG
bbox_maxlon = lons.max() + BUFFER_DEG
bbox_minlat = lats.min() - BUFFER_DEG
bbox_maxlat = lats.max() + BUFFER_DEG

with rasterio.open(DEM_URL) as src:
    print(f"DEM CRS        : {src.crs}")
    print(f"DEM Resolution : {src.res[0]:.2f}m x {src.res[1]:.2f}m")
    
    # Transform bbox to DEM CRS and read window
    t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    xmin, ymin = t.transform(bbox_minlon, bbox_minlat)
    xmax, ymax = t.transform(bbox_maxlon, bbox_maxlat)
    
    window = from_bounds(xmin, ymin, xmax, ymax, src.transform)
    dem_data   = src.read(1, window=window)
    dem_transf = src.window_transform(window)
    dem_nodata = src.nodata
    
    print(f"Window shape   : {dem_data.shape} pixels")
    print(f"Elevation range: {dem_data.min():.1f}m – {dem_data.max():.1f}m\n")

    # Sample elevation at each node
    t_to_dem = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    elevations = []
    for _, row in nodes_df.iterrows():
        x, y = t_to_dem.transform(row["lon"], row["lat"])
        # Convert projected coord to pixel row/col within window
        col = (x - dem_transf.c) / dem_transf.a
        row_idx = (y - dem_transf.f) / dem_transf.e
        col_i = int(round(col))
        row_i = int(round(row_idx))
        # Clamp to array bounds
        col_i = max(0, min(col_i, dem_data.shape[1]-1))
        row_i = max(0, min(row_i, dem_data.shape[0]-1))
        elev = dem_data[row_i, col_i]
        if dem_nodata and elev == dem_nodata:
            elev = np.nan
        elevations.append(float(elev))

nodes_df["elev_m"]      = elevations
nodes_df["elev_ft"]     = nodes_df["elev_m"] * 3.28084
nodes_df["elev_source"] = "QL1_LiDAR_35cm"

print("Node elevations (LiDAR-validated):")
print(f"  {'Node':<32} {'Elev (m)':>10} {'Elev (ft)':>10}")
print(f"  {'-'*32} {'-'*10} {'-'*10}")
for _, r in nodes_df.iterrows():
    print(f"  {r['name']:<32} {r['elev_m']:>10.1f} {r['elev_ft']:>10.1f}")

# ─────────────────────────────────────────────────────────────
# STEP 2: Densify lines and sample elevation along each segment
# ─────────────────────────────────────────────────────────────
print(f"\nDensifying lines at {DENSIFY_M}m intervals and sampling DEM...")

to_wgs  = Transformer.from_crs("EPSG:32618", "EPSG:4326",  always_xy=True)
to_utm  = Transformer.from_crs("EPSG:4326",  "EPSG:32618", always_xy=True)
to_dem  = Transformer.from_crs("EPSG:4326",  src.crs,       always_xy=True)

node_lookup = {
    r["name"]: {"lon": r["lon"], "lat": r["lat"], "elev_m": r["elev_m"]}
    for _, r in nodes_df.iterrows()
}

def sample_dem_elevation(lon, lat):
    """Sample DEM elevation at a given lon/lat."""
    x, y = to_dem.transform(lon, lat)
    col = (x - dem_transf.c) / dem_transf.a
    row_idx = (y - dem_transf.f) / dem_transf.e
    col_i = int(round(col))
    row_i = int(round(row_idx))
    col_i = max(0, min(col_i, dem_data.shape[1]-1))
    row_i = max(0, min(row_i, dem_data.shape[0]-1))
    elev = dem_data[row_i, col_i]
    return float(elev)

def calc_3d_length_dem(from_name, to_name):
    """
    Densify segment at DENSIFY_M intervals,
    sample DEM at each vertex, return true 3D length.
    """
    a = node_lookup.get(from_name)
    b = node_lookup.get(to_name)
    if not a or not b:
        return None, None, None, None

    # UTM coordinates
    ax, ay = to_utm.transform(a["lon"], a["lat"])
    bx, by = to_utm.transform(b["lon"], b["lat"])

    dist_2d = np.sqrt((bx-ax)**2 + (by-ay)**2)
    n_pts   = max(2, int(np.ceil(dist_2d / DENSIFY_M)) + 1)

    xs = np.linspace(ax, bx, n_pts)
    ys = np.linspace(ay, by, n_pts)

    # Convert each vertex back to lon/lat and sample DEM
    elevs = []
    for xi, yi in zip(xs, ys):
        lon, lat = to_wgs.transform(xi, yi)
        elevs.append(sample_dem_elevation(lon, lat))

    # Calculate cumulative 3D length
    total_3d = 0.0
    for i in range(len(xs)-1):
        dx = xs[i+1] - xs[i]
        dy = ys[i+1] - ys[i]
        dz = elevs[i+1] - elevs[i]
        total_3d += np.sqrt(dx**2 + dy**2 + dz**2)

    elev_delta  = elevs[-1] - elevs[0]
    return dist_2d, total_3d, elev_delta, n_pts

# ─────────────────────────────────────────────────────────────
# STEP 3: Build edge table with 3D lengths
# ─────────────────────────────────────────────────────────────
edge_cols = ["from_node","to_node","fiber_type","strand_count",
             "leased","defunct","segment_type","notes"]
edges_df = pd.DataFrame(edges_raw, columns=edge_cols)

rows = []
for _, r in edges_df.iterrows():
    d2, d3, dz, n = calc_3d_length_dem(r["from_node"], r["to_node"])
    rows.append((d2, d3, dz, n))

edges_df["length_2d_m"]       = [r[0] for r in rows]
edges_df["length_3d_m"]       = [r[1] for r in rows]
edges_df["elev_delta_m"]      = [r[2] for r in rows]
edges_df["vertices_sampled"]  = [r[3] for r in rows]
edges_df["length_2d_ft"]      = edges_df["length_2d_m"] * 3.28084
edges_df["length_3d_ft"]      = edges_df["length_3d_m"] * 3.28084
edges_df["length_2d_mi"]      = edges_df["length_2d_m"] / 1609.344
edges_df["length_3d_mi"]      = edges_df["length_3d_m"] / 1609.344
edges_df["elev_correction_pct"] = (
    (edges_df["length_3d_m"] - edges_df["length_2d_m"]) / 
     edges_df["length_2d_m"] * 100).round(2)
edges_df["elev_source"]       = "QL1_LiDAR_35cm"

# ─────────────────────────────────────────────────────────────
# STEP 4: Save outputs
# ─────────────────────────────────────────────────────────────
def make_line(row):
    a = node_lookup.get(row["from_node"])
    b = node_lookup.get(row["to_node"])
    if a and b:
        return LineString([(a["lon"], a["lat"]), (b["lon"], b["lat"])])

nodes_df["geometry"] = nodes_df.apply(lambda r: Point(r["lon"], r["lat"]), axis=1)
edges_df["geometry"] = edges_df.apply(make_line, axis=1)

nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry="geometry", crs="EPSG:4326")
edges_gdf = gpd.GeoDataFrame(edges_df, geometry="geometry", crs="EPSG:4326")

nodes_gdf.to_file(OUTPUT_DIR + "nodes_dem.geojson", driver="GeoJSON")
edges_gdf.to_file(OUTPUT_DIR + "edges_dem.geojson", driver="GeoJSON")
edges_df.drop("geometry", axis=1).to_csv(OUTPUT_DIR + "edges_dem.csv",  index=False)
nodes_df.drop("geometry", axis=1).to_csv(OUTPUT_DIR + "nodes_dem.csv",  index=False)

# ─────────────────────────────────────────────────────────────
# STEP 5: Print report
# ─────────────────────────────────────────────────────────────
report_lines = []
def rprint(s=""):
    print(s)
    report_lines.append(s)

rprint("=" * 65)
rprint("  STAGE 2A — 3D DISTANCE REPORT (QL1 LiDAR 35cm DEM)")
rprint("=" * 65)

for label, filt in [
    ("BURIED",     edges_df["segment_type"]=="buried"),
    ("LIFT FIBER", edges_df["segment_type"]=="lift"),
    ("LEASED",     edges_df["segment_type"]=="leased"),
]:
    grp = edges_df[filt]
    t2  = grp["length_2d_m"].sum()
    t3  = grp["length_3d_m"].sum()
    corr = (t3-t2)/t2*100 if t2 > 0 else 0
    rprint(f"\n{'─'*65}")
    rprint(f"  {label} ({len(grp)} segments)")
    rprint(f"{'─'*65}")
    rprint(f"  {'Segment':<34} {'2D(ft)':>8} {'3D(ft)':>8} {'ΔElev(ft)':>10} {'Corr%':>6}")
    for _, r in grp.iterrows():
        seg = f"{r['from_node'][:16]}→{r['to_node'][:16]}"
        rprint(f"  {seg:<34} {r['length_2d_ft']:>8.0f} {r['length_3d_ft']:>8.0f} "
               f"{r['elev_delta_m']*3.28084:>10.0f} {r['elev_correction_pct']:>5.1f}%")
    rprint(f"  {'SUBTOTAL':<34} {t2*3.28084:>8.0f} {t3*3.28084:>8.0f} {'':>10} {corr:>5.1f}%")

total_2d = edges_df["length_2d_m"].sum()
total_3d = edges_df["length_3d_m"].sum()
defunct  = edges_df[edges_df["defunct"]==True]
leased   = edges_df[edges_df["segment_type"]=="leased"]
rprint(f"\n{'='*65}")
rprint(f"  NETWORK TOTALS (QL1 LiDAR validated)")
rprint(f"{'='*65}")
rprint(f"  2D total : {total_2d:>8.0f} m | {total_2d/1609.344:.2f} mi | {total_2d*3.28084:,.0f} ft")
rprint(f"  3D total : {total_3d:>8.0f} m | {total_3d/1609.344:.2f} mi | {total_3d*3.28084:,.0f} ft")
rprint(f"  Correction: +{(total_3d-total_2d)/total_2d*100:.1f}%")
rprint(f"  Defunct  : {defunct['length_3d_m'].sum()*3.28084:.0f} ft (excluded from total)")
rprint(f"  Leased   : {leased['length_3d_m'].sum()*3.28084:,.0f} ft (not owned)")
rprint(f"\n✅ Outputs: nodes_dem.geojson, edges_dem.geojson, edges_dem.csv, nodes_dem.csv")

with open(OUTPUT_DIR + "network_report.txt", "w") as f:
    f.write("\n".join(report_lines))

print("\nDone. All files saved to:", OUTPUT_DIR)
