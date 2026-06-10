# Network Topology — Stowe Fiber Network

## Architecture Overview

The network has three primary hubs and two elevation tiers connected by lift fiber:

```
BASE VILLAGE              MOUNTAIN BASE            UPPER MOUNTAIN
──────────────            ─────────────            ──────────────
Admin (hub)  ←──leased──→ Stowe Mtn Lodge ──→ Bldg N ──→ Bldg M
    │                           │                │
    ├──→ The Inn ──→ Marketing   └──→ First Chair  └──→ Spruce Camp (hub)
    │        └──→ THCC                                      │
    └──leased──→ Warehouse                           ├──→ F.A.A.T ──→ Sunny Quad
              ├──→ FarmHouse                         │         └──→ Race Shack
              └──→ Nordic Ctr                        │              └──→ Meadows Quad
                                                     │                   └──→ Sensation Quad
                                                     │                        └──→ Turf Bldg
                                                     │                             └──→ Adv Triple
                                                     └──(via Adventure Center) ──→ ...

MOUNTAIN BASE (MOC hub)
    ├──→ Gondola Barn ──→ [lift] Cliff House
    │         ├──→ [lift] Octagon ──→ Ski Patrol (269)
    │         ├──→ Vehicles ──→ Midway ──→ Snowmaking
    │         └──→ Midway ──→ [same node]
    ├──→ Demo Center ──→ Four Runner Quad
    ├──→ Mansfield ──→ Lookout ──→ Sunrise
    ├──→ [lift] Over Easy Drive ──→ Over Easy Return ──→ Spruce Camp
    └──→ Spruce Camp (direct 12 SM buried)
```

---

## Hub Nodes

### MOC — Mountain Operations Center
- **Role:** Primary hub, mountain side
- **Elevation:** ~1,296 ft
- **Connections:** 9 outbound segments
- **Backbone:** 48-strand SM from Gondola Barn
- **Redundancy:** Two paths to Spruce Camp (direct buried + via Over Easy lift fiber)

### Spruce Camp
- **Role:** Primary hub, Spruce Peak side
- **Elevation:** ~1,936 ft
- **Connections:** 5 outbound segments
- **Key run:** 60-strand SM to F.A.A.T Building — largest strand count in network
- **Redundancy:** Two paths from MOC

### Admin
- **Role:** Primary hub, base village
- **Elevation:** ~1,280 ft
- **Connections:** 4 outbound segments
- **Vulnerability:** Both inbound runs are leased (SML → Admin)

---

## Segment Inventory

### Buried Owned (31 segments)

| From | To | Fiber | Strands | 3D Length (ft) |
|------|----|-------|---------|----------------|
| Gondola Barn | MOC | SM | 48 | 300 |
| Gondola Barn | MOC | SM | 12 | 300 |
| Spruce Camp | F.A.A.T Building | SM | 60 | 544 |
| MOC | Spruce Camp | SM | 12 | 1,597 |
| Meadows Quad → | Sensation Quad | SM | 12 | 2,020 |
| Turf Building → | Adventure Triple | SM | 0 | 2,019 |
| ... | ... | ... | ... | ... |

### Lift Fiber (6 segments)

| From | To | 3D Length (ft) | Notes |
|------|----|----------------|-------|
| Gondola Barn | Cliff House | 7,650 | Gondola lift |
| Gondola Barn | Octagon | 6,084 | Quad lift |
| Over Easy Drive | Over Easy Return | 1,606 | Over Easy lift |
| Octagon | Ski Patrol (269) | 239 | Short extension |
| MOC | Over Easy Drive | 128 | Base terminal |
| Race Shack | Meadows Quad Drive | 338 | Lift fiber |

### Leased (2 segments)

| From | To | Fiber | Strands | 3D Length (ft) | Annual Risk |
|------|----|-------|---------|----------------|-------------|
| Stowe Mountain Lodge | Admin | SM | 6 | 8,207 | High |
| Admin | Warehouse | SM | 2 | 1,878 | Medium |

### Defunct (1 segment)

| From | To | Type | Strands | Notes |
|------|----|------|---------|-------|
| MOC | Mansfield Lodge | MM | 12 | 6-strand multimode — removed from service |

---

## Node Status Definitions

| Status | Count | Meaning |
|--------|-------|---------|
| `active` | 35 | Confirmed in network diagram |
| `inferred_active` | 9 | Lift return stations — logical extension of confirmed lift runs |
| `unverified` | 3 | F.A.A.T Building, Toll Road Shack, Building Maintenance XC |

---

## Elevation Zones

| Zone | Nodes | Elev Range | Key Nodes |
|------|-------|------------|-----------|
| Base Village | 10 | 1,165–1,296 ft | Admin, Warehouse, Nordic Center |
| Mountain Base | 11 | 1,263–1,509 ft | MOC, Gondola Barn, Midway, Vehicles |
| Mid Mountain | 14 | 1,558–2,805 ft | Spruce Camp, Over Easy, Bldg M/N, SML |
| Upper Mountain | 12 | 2,789–3,609 ft | Cliff House, Octagon, Sensation Quad, Ski Patrol |

---

## Open Items / Field Verification Required

- [ ] Confirm identity of F.A.A.T Building with Mountain Ops / Snowmaking team
- [ ] Verify Toll Road Shack fiber connectivity (if any)
- [ ] Confirm Building Maintenance at Cross Country Area status
- [ ] Verify strand counts on lift fiber segments (currently logged as 0/unknown)
- [ ] Confirm TollHouse Double Drive/Return connectivity
- [ ] Run `stage2a_dem.py` locally to replace estimated elevations with QL1 LiDAR values
