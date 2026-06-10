
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
