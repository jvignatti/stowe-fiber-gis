# Network Topology — Stowe Fiber Network

**Source:** High-resolution diagram by R. Kircher, revised 5/2/26  
**Last updated:** 2026  
**Total active segments:** 41 | **Total active length:** 46,767 ft / 8.86 miles

---

## Architecture Overview

```
GONDOLA CLUSTER (Mountain Base)
    Gondola Barn
        ├──[LF]──→ Cliff House
        ├──[SM/48]──→ MOC  (primary backbone)
        ├──[SM/12]──→ MOC  (secondary run)
        └──[SM/12]──→ Midway
                         ├──[SM/12]──→ Snowmaking Control
                         │                └──[SM/12]──→ Vehicles Maintenance
                         └──[SM/12] feeds Midway only (single node)

MOC CLUSTER (Mountain Base — primary hub)
    MOC
        ├──[SM/24]──→ Demo Center
        │               ├──[SM/12]──→ Four Runner Quad Drive
        │               │               └──[LF]──→ Octagon
        │               │                           └──[LF]──→ Ski Patrol (269)
        │               └──[SM/12]──→ Lookout Double Drive
        ├──[SM/12]──→ Mansfield Lodge
        ├──[MM/12]──→ Mansfield Lodge (parallel run)
        │               └──[SM]──→ Sunrise Drive
        ├──[LF/12]──→ Over Easy Drive
        │               └──[LF]──→ Over Easy Return
        │                           └──[SM/12]──→ Spruce Camp
        ├──[SM/12]──→ Spruce Camp (direct buried — redundant path)
        └──[MM/6]──→ The Inn  *** DEFUNCT ***

SPRUCE CAMP CLUSTER (Mid Mountain — primary hub)
    Spruce Camp
        ├── UPPER
        │   ├──[SM/12]──→ F.A.A.T Building (First Aid Building Ski Patrol)
        │   └──[SM/60]──→ Sunny Quad Drive
        │                   ├──[SM/12]──→ Race Shack
        │                   ├──[SM/12]──→ Meadows Quad Drive
        │                   ├──[SM/12]──→ Adventure Triple Drive
        │                   └──[SM/12]──→ Sensation Quad Drive
        │                                   ├──[SM/?]──→ Turf Building (strands unknown)
        │                                   └──[LF]──→ Ski Patrol Spruce Side
        │
        │  (Sunny Quad Return)──[LF]──→ Ski Patrol Spruce Side
        └── LOWER
            ├──[SM/12]──→ Bldg M (Stowe Logo Store)
            ├──[SM/12]──→ Bldg N (True North)
            ├──[SM/24]──→ Adventure Center
            └──[SM/?]──→ Stowe Mountain Lodge / Hyatt (strands unknown)
                            ├──[MM/6]──→ First Chair
                            ├──[SM/10]──→ Admin  *** LEASED ***
                            └──[SM/24]──→ Adventure Center

BASE VILLAGE CLUSTER (Admin hub — primary hub)
    Admin
        ├──[SM/12]──→ The Inn
        ├──[MM/12]──→ The Inn (parallel run)
        │               └──[SM/12]──→ Marketing
        │                               └──[SM/12]──→ THCC
        └──[SM/2]──→ Warehouse  *** LEASED ***
                        ├──[SM/12]──→ FarmHouse
                        └──[SM/12]──→ Nordic Center
```

---

## Primary Hubs

| Hub | Elevation | Inbound capacity | Role |
|-----|-----------|-----------------|------|
| MOC | ~1,296 ft | 60 SM from Gondola Barn | Mountain base distribution |
| Spruce Camp | ~1,936 ft | 12 SM from MOC (×2 paths) | Spruce Peak distribution |
| Admin | ~1,280 ft | 6 SM leased from SML | Base village distribution |

---

## Segment Inventory by Type

| Type | Segments | Notes |
|------|----------|-------|
| SM buried — owned | 29 | Standard active runs |
| Lift fiber (LF) | 7 | Aerial — follows lift cable geometry |
| MM buried — owned | 3 | MOC→Mansfield (×2), Admin→The Inn |
| SM buried — leased | 2 | SML→Admin (6 SM), Admin→Warehouse (2 SM) |
| MM buried — defunct | 1 | MOC→The Inn (6 MM, 8,979 ft) |
| **Total** | **42** | 41 active + 1 defunct |

---

## Strand Count Highlights

| Segment | Strands | Notes |
|---------|---------|-------|
| Gondola Barn → MOC | 48 SM | Primary backbone |
| Spruce Camp → Sunny Quad | 60 SM | Largest Spruce side run |
| MOC → Demo Center | 24 SM | |
| Spruce Camp → Adventure Center | 24 SM | |
| SML → Admin | 6 SM leased | Sole path to Admin — highest risk |
| Admin → Warehouse | 2 SM leased | Low capacity |

### Unknown strand counts — field verification needed
- Mansfield Lodge → Sunrise Drive
- Spruce Camp → Stowe Mountain Lodge
- Sensation Quad Drive → Turf Building
- All lift fiber segments (LF)

---

## Leased Segments

Both are the sole inbound path to their downstream cluster. No owned redundancy exists.

| Segment | Strands | Length (3D) |
|---------|---------|-------------|
| SML → Admin | 6 SM | 8,207 ft |
| Admin → Warehouse | 2 SM | 1,878 ft |

Lessor SLA status unknown — verify with Vail Procurement.

---

## Defunct Segment

| Segment | Type | Length | Notes |
|---------|------|--------|-------|
| MOC → The Inn | MM / 6 | 8,979 ft / 1.70 mi | Out of service. Original backbone. Confirmed multi-mode per fiber map (R. Kircher). |

---

## Node Aliases

| Dataset name | Known as |
|---|---|
| Bldg M (Stowe Logo Store) | Logo Store (operating name) |
| Bldg N (True North) | True North (operating name) |
| Stowe Mountain Lodge | Hyatt (operating name) |
| F.A.A.T Building | First Aid Building Ski Patrol — confirmed per fiber map |
| Ski Patrol (269) | Also referenced as Bldg 269 |

---

## Open Items — Field Verification Required

| Item | Priority | Who to ask |
|------|----------|-----------|
| Leased segment SLA and contract terms | High | Vail Procurement |
| Strand counts: Mansfield→Sunrise, Spruce→SML, Sensation→Turf, all LF | Medium | Field check / Lift Maintenance |
| Toll Road Shack — fiber connection? | Low | Mountain Ops |
| Building Maintenance XC — active or historical? | Low | Mountain Ops |
| LiDAR elevation validation | Low | Run `scripts/stage2a_dem.py` locally |
