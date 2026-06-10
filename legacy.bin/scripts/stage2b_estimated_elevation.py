import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from pyproj import Transformer

# ─────────────────────────────────────────────────────────────
# NODES with estimated elevations (meters)
# Source: Stowe terrain knowledge + published resort data
# QL1 LiDAR validation pending (see stage2a_dem.py)
# ─────────────────────────────────────────────────────────────
nodes_raw = [
    # name, lat, lon, zone, status, elev_m (estimated)
    ("Vehicles Maintenance",        44.53397478022453,  -72.78970406216413, "Mountain Base",    "active",           430),
    ("Snowmaking Control",          44.53291282175362,  -72.79019935725232, "Mountain Base",    "active",           420),
    ("Midway",                      44.53168034157372,  -72.79030874148611, "Mountain Base",    "active",           460),
    ("Cliff House",                 44.53760695156738,  -72.81426928408973, "Upper Mountain",   "active",           1050),
    ("Gondola Barn",                44.53117296598019,  -72.78758861126525, "Mountain Base",    "active",           395),
    ("MOC",                         44.53045706260745,  -72.78702517521394, "Mountain Base",    "active",           395),
    ("Over Easy Drive",             44.53065375182360,  -72.78743026736026, "Mountain Base",    "active",           395),
    ("Over Easy Return",            44.53061933757054,  -72.78173001274592, "Mid Mountain",     "active",           580),
    ("Spruce Camp",                 44.53095040595042,  -72.78145485167710, "Mid Mountain",     "active",           590),
    ("Demo Center",                 44.52877056172229,  -72.78592450609574, "Mountain Base",    "active",           380),
    ("Four Runner Quad Drive",      44.52887782683637,  -72.78619393875799, "Mountain Base",    "active",           385),
    ("Four Runner Quad Return",     44.52394935565263,  -72.80786026300211, "Upper Mountain",   "inferred_active",  970),
    ("Octagon",                     44.52424278249422,  -72.80751887354039, "Upper Mountain",   "active",           975),
    ("Ski Patrol (269)",            44.52379475357288,  -72.80818265053907, "Upper Mountain",   "active",           980),
    ("Lookout Double",              44.52830091154923,  -72.78451356020577, "Mountain Base",    "active",           400),
    ("Mansfield Lodge",             44.52906754186289,  -72.78429138980584, "Mountain Base",    "active",           405),
    ("Sunrise Drive",               44.52851954600344,  -72.78323016039246, "Mountain Base",    "active",           400),
    ("Sunny Quad Drive",            44.53146202580196,  -72.78129132378108, "Mid Mountain",     "active",           620),
    ("Race Shack",                  44.53146202580196,  -72.78129132378108, "Mid Mountain",     "active",           625),
    ("Meadows Quad Drive",          44.53169465471388,  -72.78007672306560, "Mid Mountain",     "active",           650),
    ("Adventure Triple Drive",      44.53104047669733,  -72.77959711049780, "Mid Mountain",     "active",           660),
    ("Sensation Quad Drive",        44.53589261484200,  -72.77568923363755, "Upper Mountain",   "active",           850),
    ("Sensation Quad Return",       44.55097682958558,  -72.78121081469202, "Upper Mountain",   "inferred_active",  1100),
    ("Ski Patrol Spruce Side",      44.55140830106051,  -72.78123421444815, "Upper Mountain",   "active",           1100),
    ("Turf Building",               44.53560025354428,  -72.77595118335974, "Mid Mountain",     "active",           855),
    ("Bldg M",                      44.53044232708503,  -72.78084811817001, "Mid Mountain",     "active",           530),
    ("Bldg N",                      44.52983679413696,  -72.78087623427068, "Mid Mountain",     "active",           510),
    ("Adventure Center",            44.53067360086118,  -72.77995143399957, "Mid Mountain",     "active",           520),
    ("Stowe Mountain Lodge",        44.53008098184256,  -72.78105857921837, "Mid Mountain",     "active",           475),
    ("First Chair",                 44.53024775750400,  -72.78078325489172, "Mid Mountain",     "active",           480),
    ("Admin",                       44.51051810230879,  -72.76552349656498, "Base Village",     "active",           390),
    ("The Inn",                     44.51112282588134,  -72.76569787909460, "Base Village",     "active",           392),
    ("Marketing",                   44.51094463299796,  -72.76648460883614, "Base Village",     "active",           391),
    ("THCC",                        44.51034183585563,  -72.76668958805115, "Base Village",     "active",           390),
    ("Warehouse",                   44.50631448179338,  -72.76137472662325, "Base Village",     "active",           368),
    ("Nordic Center",               44.50543876655190,  -72.76256979955778, "Base Village",     "active",           360),
    ("FarmHouse",                   44.50605926131790,  -72.76097089707389, "Base Village",     "active",           365),
    ("Toll Road Shack",             44.51070875298394,  -72.76668338589920, "Base Village",     "unverified",       392),
    ("TollHouse Double Drive",      44.51079107926899,  -72.76746916540010, "Base Village",     "inferred_active",  393),
    ("TollHouse Double Return",     44.51904760482018,  -72.78883640755843, "Mountain Base",    "inferred_active",  700),
    ("Sunrise Return",              44.52055090164348,  -72.79564819987432, "Mountain Base",    "inferred_active",  700),
    ("Lookout Return",              44.52301019092231,  -72.80209924457878, "Upper Mountain",   "inferred_active",  850),
    ("Sunny Quad Return",           44.54143198244539,  -72.78284681685732, "Upper Mountain",   "inferred_active",  1000),
    ("Meadows Quad Return",         44.53626281034168,  -72.78067286470414, "Mid Mountain",     "inferred_active",  900),
    ("Adventure Triple Return",     44.53205987974514,  -72.77621440117946, "Mid Mountain",     "inferred_active",  850),
    ("Building Maintenance XC",     44.50460989564515,  -72.76287664312079, "Base Village",     "unverified",       355),
    ("F.A.A.T Building",            44.53200000000000,  -72.78050000000000, "Mid Mountain",     "unverified",       680),
]

# ─────────────────────────────────────────────────────────────
# EDGES
# ─────────────────────────────────────────────────────────────
edges_raw = [
    ("Vehicles Maintenance",    "Midway",                   "SM", 12,  False, False, "buried",  ""),
    ("Midway",                  "Snowmaking Control",        "SM", 12,  False, False, "buried",  ""),
    ("Midway",                  "Gondola Barn",              "SM", 12,  False, False, "buried",  ""),
    ("Gondola Barn",            "MOC",                       "SM", 48,  False, False, "buried",  "Primary backbone"),
    ("Gondola Barn",            "MOC",                       "SM", 12,  False, False, "buried",  "Secondary run"),
    ("Gondola Barn",            "Cliff House",               "LF", 0,   False, False, "lift",    "Lift fiber - gondola"),
    ("Gondola Barn",            "Octagon",                   "LF", 0,   False, False, "lift",    "Lift fiber"),
    ("Octagon",                 "Ski Patrol (269)",          "LF", 0,   False, False, "lift",    "Lift fiber"),
    ("Gondola Barn",            "Four Runner Quad Drive",    "SM", 12,  False, False, "buried",  ""),
    ("Four Runner Quad Drive",  "Demo Center",               "SM", 12,  False, False, "buried",  ""),
    ("Demo Center",             "MOC",                       "SM", 24,  False, False, "buried",  ""),
    ("MOC",                     "Over Easy Drive",           "LF", 12,  False, False, "lift",    "Lift fiber + 12 SM"),
    ("Over Easy Drive",         "Over Easy Return",          "LF", 0,   False, False, "lift",    "Lift fiber"),
    ("Over Easy Return",        "Spruce Camp",               "SM", 12,  False, False, "buried",  ""),
    ("MOC",                     "Spruce Camp",               "SM", 12,  False, False, "buried",  "Direct run"),
    ("MOC",                     "Mansfield Lodge",           "SM", 12,  False, False, "buried",  ""),
    ("MOC",                     "Mansfield Lodge",           "MM", 12,  False, True,  "buried",  "6-strand multimode defunct"),
    ("Mansfield Lodge",         "Lookout Double",            "SM", 0,   False, False, "buried",  ""),
    ("Lookout Double",          "Sunrise Drive",             "SM", 0,   False, False, "buried",  ""),
    ("Spruce Camp",             "F.A.A.T Building",          "SM", 60,  False, False, "buried",  "Likely snowmaking hub"),
    ("F.A.A.T Building",        "Sunny Quad Drive",          "SM", 12,  False, False, "buried",  ""),
    ("Sunny Quad Drive",        "Race Shack",                "SM", 12,  False, False, "buried",  ""),
    ("Race Shack",              "Meadows Quad Drive",        "LF", 12,  False, False, "lift",    "Lift fiber"),
    ("Meadows Quad Drive",      "Sensation Quad Drive",      "SM", 12,  False, False, "buried",  ""),
    ("Sensation Quad Drive",    "Turf Building",             "SM", 12,  False, False, "buried",  ""),
    ("Turf Building",           "Adventure Triple Drive",    "SM", 0,   False, False, "buried",  ""),
    ("Spruce Camp",             "Bldg M",                    "SM", 12,  False, False, "buried",  ""),
    ("Bldg M",                  "Bldg N",                    "SM", 12,  False, False, "buried",  ""),
    ("Bldg N",                  "Adventure Center",          "SM", 24,  False, False, "buried",  ""),
    ("Bldg N",                  "Stowe Mountain Lodge",      "SM", 0,   False, False, "buried",  ""),
    ("Stowe Mountain Lodge",    "First Chair",               "MM", 6,   False, False, "buried",  ""),
    ("Stowe Mountain Lodge",    "Admin",                     "SM", 6,   True,  False, "leased",  "6 strand SM leased"),
    ("Admin",                   "The Inn",                   "SM", 12,  False, False, "buried",  ""),
    ("Admin",                   "The Inn",                   "MM", 12,  False, False, "buried",  ""),
    ("The Inn",                 "Marketing",                 "SM", 12,  False, False, "buried",  ""),
    ("Marketing",               "THCC",                      "SM", 12,  False, False, "buried",  ""),
    ("Admin",                   "Warehouse",                 "SM", 2,   True,  False, "leased",  "2 strand SM leased"),
    ("Warehouse",               "FarmHouse",                 "SM", 12,  False, False, "buried",  ""),
    ("Warehouse",               "Nordic Center",             "SM", 12,  False, False, "buried",  ""),
]

# ─────────────────────────────────────────────────────────────
# BUILD NODE LOOKUP
# ─────────────────────────────────────────────────────────────
node_cols = ["name","lat","lon","zone","status","elev_m"]
nodes_df  = pd.DataFrame(nodes_raw, columns=node_cols)
nodes_df["elev_source"] = "estimated"

node_lookup = {
    r["name"]: {"lon": r["lon"], "lat": r["lat"], "elev_m": r["elev_m"]}
    for _, r in nodes_df.iterrows()
}

# ─────────────────────────────────────────────────────────────
# 3D DISTANCE FUNCTION
# Projects to UTM 18N, adds Z, returns true 3D length in meters
# ─────────────────────────────────────────────────────────────
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)

def calc_3d_length(from_name, to_name):
    a = node_lookup.get(from_name)
    b = node_lookup.get(to_name)
    if not a or not b:
        return None, None, None

    ax, ay = transformer.transform(a["lon"], a["lat"])
    bx, by = transformer.transform(b["lon"], b["lat"])
    az, bz = a["elev_m"], b["elev_m"]

    dx = bx - ax
    dy = by - ay
    dz = bz - az

    dist_2d = np.sqrt(dx**2 + dy**2)
    dist_3d = np.sqrt(dx**2 + dy**2 + dz**2)
    elev_delta = bz - az

    return dist_2d, dist_3d, elev_delta

# ─────────────────────────────────────────────────────────────
# BUILD EDGES
# ─────────────────────────────────────────────────────────────
edge_cols = ["from_node","to_node","fiber_type","strand_count",
             "leased","defunct","segment_type","notes"]
edges_df = pd.DataFrame(edges_raw, columns=edge_cols)

results = [calc_3d_length(r["from_node"], r["to_node"]) for _, r in edges_df.iterrows()]
edges_df["length_2d_m"]  = [r[0] for r in results]
edges_df["length_3d_m"]  = [r[1] for r in results]
edges_df["elev_delta_m"] = [r[2] for r in results]
edges_df["length_2d_ft"] = edges_df["length_2d_m"] * 3.28084
edges_df["length_3d_ft"] = edges_df["length_3d_m"] * 3.28084
edges_df["length_2d_mi"] = edges_df["length_2d_m"] / 1609.344
edges_df["length_3d_mi"] = edges_df["length_3d_m"] / 1609.344
edges_df["elev_correction_pct"] = (
    (edges_df["length_3d_m"] - edges_df["length_2d_m"]) / edges_df["length_2d_m"] * 100
).round(2)
edges_df["elev_source"] = "estimated"

# ─────────────────────────────────────────────────────────────
# GEOJSON OUTPUT
# ─────────────────────────────────────────────────────────────
def make_line(row):
    a = node_lookup.get(row["from_node"])
    b = node_lookup.get(row["to_node"])
    if a and b:
        return LineString([(a["lon"], a["lat"]), (b["lon"], b["lat"])])
    return None

edges_df["geometry"] = edges_df.apply(make_line, axis=1)
edges_gdf = gpd.GeoDataFrame(edges_df, geometry="geometry", crs="EPSG:4326")

nodes_df["geometry"] = nodes_df.apply(
    lambda r: Point(r["lon"], r["lat"]), axis=1)
nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry="geometry", crs="EPSG:4326")

nodes_gdf.to_file("/home/claude/fiber/nodes_3d.geojson", driver="GeoJSON")
edges_gdf.to_file("/home/claude/fiber/edges_3d.geojson", driver="GeoJSON")
edges_df.drop("geometry", axis=1).to_csv("/home/claude/fiber/edges_3d.csv", index=False)
nodes_df.drop("geometry", axis=1).to_csv("/home/claude/fiber/nodes_3d.csv", index=False)

# ─────────────────────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────────────────────
FT_PER_MILE = 5280

print("=" * 62)
print("  STAGE 2B — 3D DISTANCE REPORT (estimated elevations)")
print("=" * 62)

buried  = edges_df[edges_df["segment_type"] == "buried"]
lift    = edges_df[edges_df["segment_type"] == "lift"]
leased  = edges_df[edges_df["segment_type"] == "leased"]
defunct = edges_df[edges_df["defunct"] == True]

for label, grp in [("Buried", buried), ("Lift Fiber", lift), ("Leased", leased)]:
    t2 = grp["length_2d_m"].sum()
    t3 = grp["length_3d_m"].sum()
    corr = (t3 - t2) / t2 * 100 if t2 > 0 else 0
    print(f"\n{'─'*62}")
    print(f"  {label.upper()} SEGMENTS ({len(grp)} segments)")
    print(f"{'─'*62}")
    print(f"  {'Segment':<32} {'2D(ft)':>8} {'3D(ft)':>8} {'ΔElev(ft)':>10} {'Corr%':>6}")
    print(f"  {'-'*32} {'-'*8} {'-'*8} {'-'*10} {'-'*6}")
    for _, r in grp.iterrows():
        seg = f"{r['from_node'][:16]}→{r['to_node'][:14]}"
        print(f"  {seg:<32} {r['length_2d_ft']:>8.0f} {r['length_3d_ft']:>8.0f} "
              f"{r['elev_delta_m']*3.28084:>10.0f} {r['elev_correction_pct']:>5.1f}%")
    print(f"  {'SUBTOTAL':<32} {t2*3.28084:>8.0f} {t3*3.28084:>8.0f} "
          f"{'':>10} {corr:>5.1f}%")

total_2d = edges_df["length_2d_m"].sum()
total_3d = edges_df["length_3d_m"].sum()
total_corr = (total_3d - total_2d) / total_2d * 100

print(f"\n{'=' * 62}")
print(f"  NETWORK TOTALS")
print(f"{'=' * 62}")
print(f"  2D (flat-earth) total : {total_2d:>8.0f} m  |  {total_2d/1609.344:.2f} miles  |  {total_2d*3.28084:,.0f} ft")
print(f"  3D (with elevation)   : {total_3d:>8.0f} m  |  {total_3d/1609.344:.2f} miles  |  {total_3d*3.28084:,.0f} ft")
print(f"  Elevation correction  : +{total_corr:.1f}%  ({(total_3d-total_2d)*3.28084:,.0f} ft added)")
print(f"\n  Defunct (excluded)    : {defunct['length_3d_m'].sum()*3.28084:.0f} ft")
print(f"  Leased (not owned)    : {leased['length_3d_m'].sum()*3.28084:,.0f} ft")

print(f"\n  ⚠️  Elevations are ESTIMATED from terrain knowledge.")
print(f"      Run stage2a_dem.py locally for LiDAR-validated lengths.")
print(f"\n✅  Files: nodes_3d.geojson, edges_3d.geojson, edges_3d.csv, nodes_3d.csv")
