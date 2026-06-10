import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import json

# ─────────────────────────────────────────────
# NODES
# ─────────────────────────────────────────────
nodes_raw = [
    # name, lat, lon, zone, status
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
    ("F.A.A.T Building",            44.53146202580196,  -72.78129132378108, "Mid Mountain",     "active"),  # Near Spruce Camp cluster
]

# ─────────────────────────────────────────────
# EDGES
# fiber_type: SM=single-mode, MM=multi-mode, LF=lift fiber
# strand_count: number of strands
# leased: True/False
# defunct: True/False
# segment_type: buried, lift, leased
# ─────────────────────────────────────────────
edges_raw = [
    # (from, to, fiber_type, strand_count, leased, defunct, segment_type, notes)
    ("Vehicles Maintenance",    "Midway",               "SM", 12,  False, False, "buried",  ""),
    ("Midway",                  "Snowmaking Control",   "SM", 12,  False, False, "buried",  ""),
    ("Midway",                  "Gondola Barn",         "SM", 12,  False, False, "buried",  ""),
    ("Gondola Barn",            "MOC",                  "SM", 48,  False, False, "buried",  "Primary backbone"),
    ("Gondola Barn",            "MOC",                  "SM", 12,  False, False, "buried",  "Secondary run"),
    ("Gondola Barn",            "Cliff House",          "LF", 0,   False, False, "lift",    "Lift fiber - gondola"),
    ("Gondola Barn",            "Octagon",              "LF", 0,   False, False, "lift",    "Lift fiber"),
    ("Octagon",                 "Ski Patrol (269)",     "LF", 0,   False, False, "lift",    "Lift fiber"),
    ("Gondola Barn",            "Four Runner Quad Drive","SM",12,  False, False, "buried",  ""),
    ("Four Runner Quad Drive",  "Demo Center",          "SM", 12,  False, False, "buried",  ""),
    ("Demo Center",             "MOC",                  "SM", 24,  False, False, "buried",  ""),
    ("MOC",                     "Over Easy Drive",      "LF", 12,  False, False, "lift",    "Lift fiber + 12 SM"),
    ("Over Easy Drive",         "Over Easy Return",     "LF", 0,   False, False, "lift",    "Lift fiber"),
    ("Over Easy Return",        "Spruce Camp",          "SM", 12,  False, False, "buried",  ""),
    ("MOC",                     "Spruce Camp",          "SM", 12,  False, False, "buried",  "Direct run"),
    ("MOC",                     "Mansfield Lodge",      "SM", 12,  False, False, "buried",  ""),
    ("MOC",                     "Mansfield Lodge",      "MM", 12,  False, True,  "buried",  "6-strand multimode defunct"),
    ("Mansfield Lodge",         "Lookout Double",       "SM", 0,   False, False, "buried",  ""),
    ("Lookout Double",          "Sunrise Drive",        "SM", 0,   False, False, "buried",  ""),
    ("Spruce Camp",             "F.A.A.T Building",     "SM", 60,  False, False, "buried",  ""),
    ("F.A.A.T Building",        "Sunny Quad Drive",     "SM", 12,  False, False, "buried",  ""),
    ("Sunny Quad Drive",        "Race Shack",           "SM", 12,  False, False, "buried",  ""),
    ("Race Shack",              "Meadows Quad Drive",   "LF", 12,  False, False, "lift",    "Lift fiber"),
    ("Meadows Quad Drive",      "Sensation Quad Drive", "SM", 12,  False, False, "buried",  ""),
    ("Sensation Quad Drive",    "Turf Building",        "SM", 12,  False, False, "buried",  ""),
    ("Turf Building",           "Adventure Triple Drive","SM",0,   False, False, "buried",  ""),
    ("Spruce Camp",             "Bldg M",               "SM", 12,  False, False, "buried",  ""),
    ("Bldg M",                  "Bldg N",               "SM", 12,  False, False, "buried",  ""),
    ("Bldg N",                  "Adventure Center",     "SM", 24,  False, False, "buried",  ""),
    ("Bldg N",                  "Stowe Mountain Lodge", "SM", 0,   False, False, "buried",  ""),
    ("Stowe Mountain Lodge",    "First Chair",          "MM", 6,   False, False, "buried",  ""),
    ("Stowe Mountain Lodge",    "Admin",                "SM", 6,   True,  False, "leased",  "6 strand SM leased"),
    ("Admin",                   "The Inn",              "SM", 12,  False, False, "buried",  ""),
    ("Admin",                   "The Inn",              "MM", 12,  False, False, "buried",  ""),
    ("The Inn",                 "Marketing",            "SM", 12,  False, False, "buried",  ""),
    ("Marketing",               "THCC",                 "SM", 12,  False, False, "buried",  ""),
    ("Admin",                   "Warehouse",            "SM", 2,   True,  False, "leased",  "2 strand SM leased"),
    ("Warehouse",               "FarmHouse",            "SM", 12,  False, False, "buried",  ""),
    ("Warehouse",               "Nordic Center",        "SM", 12,  False, False, "buried",  ""),
]

# ─────────────────────────────────────────────
# BUILD GEODATAFRAMES
# ─────────────────────────────────────────────
node_cols = ["name","lat","lon","zone","status"]
nodes_df = pd.DataFrame(nodes_raw, columns=node_cols)
nodes_df["geometry"] = nodes_df.apply(lambda r: Point(r.lon, r.lat), axis=1)
nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry="geometry", crs="EPSG:4326")

# Build lookup
node_lookup = {row["name"]: (row["lon"], row["lat"]) for _, row in nodes_df.iterrows()}

# Build edges
edge_cols = ["from_node","to_node","fiber_type","strand_count","leased","defunct","segment_type","notes"]
edges_df = pd.DataFrame(edges_raw, columns=edge_cols)

def make_line(row):
    a = node_lookup.get(row["from_node"])
    b = node_lookup.get(row["to_node"])
    if a and b:
        return LineString([a, b])
    return None

edges_df["geometry"] = edges_df.apply(make_line, axis=1)
edges_gdf = gpd.GeoDataFrame(edges_df, geometry="geometry", crs="EPSG:4326")

# Calculate 2D geodesic length in meters
edges_gdf_proj = edges_gdf.to_crs("EPSG:32618")  # UTM Zone 18N - Vermont
edges_gdf["length_2d_m"] = edges_gdf_proj.geometry.length
edges_gdf["length_2d_ft"] = edges_gdf["length_2d_m"] * 3.28084

# ─────────────────────────────────────────────
# SAVE OUTPUTS
# ─────────────────────────────────────────────
nodes_gdf.to_file("/home/claude/fiber/nodes.geojson", driver="GeoJSON")
edges_gdf.to_file("/home/claude/fiber/edges.geojson", driver="GeoJSON")
nodes_df.drop("geometry", axis=1).to_csv("/home/claude/fiber/nodes.csv", index=False)
edges_df.drop("geometry", axis=1).to_csv("/home/claude/fiber/edges.csv", index=False)

# ─────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────
print("=" * 55)
print("STAGE 1 — NODES & EDGES SUMMARY")
print("=" * 55)

print(f"\n📍 NODES: {len(nodes_gdf)} total")
for status, grp in nodes_gdf.groupby("status"):
    print(f"   {status:20s}: {len(grp)}")

print(f"\n🔗 EDGES: {len(edges_gdf)} total")
for seg, grp in edges_gdf.groupby("segment_type"):
    total_m = grp["length_2d_m"].sum()
    print(f"   {seg:10s}: {len(grp):2d} segments  |  {total_m:8.0f} m  |  {total_m*3.28084/5280:.2f} miles (2D)")

print(f"\n📊 FIBER TYPE BREAKDOWN:")
for ft, grp in edges_gdf.groupby("fiber_type"):
    label = {"SM":"Single-Mode","MM":"Multi-Mode","LF":"Lift Fiber"}.get(ft, ft)
    print(f"   {label:15s}: {len(grp):2d} segments")

leased = edges_gdf[edges_gdf["leased"]==True]
defunct = edges_gdf[edges_gdf["defunct"]==True]
print(f"\n⚠️  Leased segments : {len(leased)}  ({leased['length_2d_m'].sum():.0f} m)")
print(f"⚠️  Defunct segments: {len(defunct)}  ({defunct['length_2d_m'].sum():.0f} m)")

total_2d = edges_gdf["length_2d_m"].sum()
print(f"\n📏 TOTAL NETWORK (2D no-elevation): {total_2d:.0f} m  |  {total_2d*3.28084/5280:.2f} miles")
print("\n✅ Files saved: nodes.geojson, edges.geojson, nodes.csv, edges.csv")
