# Business Analysis & Recommendations

**Stowe Mountain Resort — Fiber Network**  
**Prepared by:** JC Vignatti, Mountain Operations  
**Date:** 2026

---

## Question 1 — What Is the Actual Fiber Length?

### Answer

| Measurement | Value |
|-------------|-------|
| **Total network — 3D with elevation** | **41,475 ft / 7.86 miles** |
| Owned fiber (3D) | 31,390 ft / 5.94 miles |
| Leased fiber (3D) | 10,085 ft / 1.91 miles |
| Lift fiber (3D) | 16,045 ft / 3.04 miles |
| Buried owned (3D) | 15,346 ft / 2.91 miles |
| Defunct segment | 875 ft (excluded from total) |

### Why This Number Differs From a Flat Map

Stowe spans **2,444 ft of vertical relief** (1,165 ft at Nordic Center to 3,609 ft at Ski Patrol Spruce Side). A flat 2D measurement underestimates every segment that climbs or descends. The overall elevation correction for this network is **+3.7%** — meaning the flat map would show 7.58 miles but the true cable requirement is 7.86 miles.

High-correction segments to note:

| Segment | 2D (ft) | 3D (ft) | Correction |
|---------|---------|---------|------------|
| Bldg N → Stowe Mountain Lodge | 101 | 153 | +51.5% |
| Spruce Camp → Bldg M | 244 | 313 | +28.6% |
| F.A.A.T → Sunny Quad Drive | 285 | 346 | +21.6% |
| Spruce Camp → F.A.A.T | 457 | 544 | +19.1% |
| MOC → Spruce Camp (direct) | 1,464 | 1,597 | +9.1% |

> **⚠️ Elevation data note:** Current values are estimated from terrain knowledge. Run `stage2a_dem.py` locally against Vermont's QL1 LiDAR DEM (35cm resolution) for final validated values. Expected variance: ±5–10% on steep segments.

---

## Question 2 — Own vs. Lease: Cost of Current Leases vs. Investing

### Current Leased Segments

| Segment | Length | Strands | Monthly Est. | Annual Est. |
|---------|--------|---------|--------------|-------------|
| SML → Admin | 8,207 ft (1.55 mi) | 6 SM | $800–$1,400 | $9,600–$16,800 |
| Admin → Warehouse | 1,878 ft (0.36 mi) | 2 SM | $200–$400 | $2,400–$4,800 |
| **Total leased** | **10,085 ft (1.91 mi)** | | **$1,000–$1,800/mo** | **$12,000–$21,600/yr** |

> Note: Actual lease costs should be pulled from Vail Resorts finance/procurement. Ranges above are based on Vermont commercial dark fiber market rates for rural/mountain installations.

### Cost to Own: Capital Investment Estimate

Replacing the two leased segments with owned buried fiber:

| Item | Unit | Qty | Est. Unit Cost | Total |
|------|------|-----|----------------|-------|
| Directional boring / trenching | per linear ft | 10,085 ft | $35–$65/ft | $353k–$655k |
| 12-strand SM cable | per ft | 10,085 ft | $1.50/ft | $15k |
| Splicing & termination | per splice point | ~6 | $500 | $3k |
| Conduit (HDPE) | per ft | 10,085 ft | $1.20/ft | $12k |
| Permitting / ROW (Stowe village road) | lump sum | — | $15k–$40k | $15k–$40k |
| Project management + engineering | % of construction | 15% | — | $57k–$107k |
| **Total capital estimate** | | | | **$455k–$832k** |

### Simple Payback Analysis

| Scenario | Annual Lease Cost | Capital Cost | Payback Period |
|----------|------------------|--------------|----------------|
| Low end | $12,000/yr | $455,000 | **~38 years** |
| Mid estimate | $17,000/yr | $643,000 | **~38 years** |
| High end | $21,600/yr | $832,000 | **~39 years** |

### Recommendation

**At current lease rates, ownership does not pencil out on pure payback.** The capital required to bury 1.9 miles through Stowe village and mountain access roads vastly exceeds the lease cost savings within any reasonable infrastructure cycle (10–15 years).

**However, ownership becomes compelling if:**

- Lease rates increase (renegotiation risk at contract renewal)
- The SML → Admin segment is at risk of non-renewal (vendor relationship)
- A major network expansion is planned that would use the same trench/conduit (incremental cost drops significantly)
- Vail Resorts consolidates fiber contracts regionally and can negotiate a volume build

**Recommended action:** Audit current lease contract terms (expiration date, renewal clauses, rate escalators). If renewal is within 2–3 years, begin capacity planning conversations with Vail IT and the lessor simultaneously. Request current annual spend from Finance to replace the estimated figures above.

---

## Question 3 — Catastrophic Failure Scenario: What Does a Severed Critical Segment Cost?

### Most Critical Single Points of Failure

The network has two segments whose failure cascades to the largest portion of the resort:

#### Scenario A — MOC → Spruce Camp Direct Run (12 SM, 1,597 ft) Severed

**What goes down:**
- Spruce Camp hub loses its direct buried path from MOC
- Redundancy path exists via Over Easy lift fiber — but lift fiber is:
  - Exposed and weather-dependent
  - Not designed for sustained primary traffic
  - Unavailable if the Over Easy lift is down (maintenance, wind hold, etc.)

**If redundancy also fails (double failure — lift down + buried cut):**

| System | Status | Impact |
|--------|--------|--------|
| Spruce Camp hub | Offline | All downstream nodes dark |
| F.A.A.T / Snowmaking upper | Offline | Snowgun control lost — upper mountain snowmaking halted |
| Sunny Quad, Race Shack, Meadows Quad, Sensation Quad | Offline | Lift control / communications down |
| Adventure Triple, Turf Building | Offline | Communications down |
| Bldg M, Bldg N, Adventure Center | Offline | Guest services offline |
| Stowe Mountain Lodge systems | Degraded | Dependency on Bldg N path |

**Revenue impact — peak week (Presidents' Week / Holiday):**

| Metric | Stowe estimate |
|--------|---------------|
| Skier visits on a peak day | ~5,000–6,500 |
| Average ticket value (2026) | ~$200 |
| Daily lift revenue | $1.0M–$1.3M |
| Ancillary (food, rental, lessons) | ~30–40% of lift | $300k–$520k |
| **Total peak day revenue** | | **$1.3M–$1.8M/day** |

If Spruce Peak side lifts cannot operate due to loss of lift control connectivity:
- Approx. 40–50% of skiable terrain is on the Spruce side
- Partial closure scenario (Mansfield still runs via Gondola): **$400k–$700k/day** lost
- Full connectivity failure (all systems down): **up to $1.8M/day**

**Estimated restoration time:** 4–8 hours if crew and materials are pre-staged. 24–48 hours if excavation is required in frozen ground.

**Worst case (Presidents' Week, 3-day outage):** $1.2M–$5.4M total impact.

#### Scenario B — SML → Admin Leased Segment Severed

**What goes down:**
- Admin hub loses its upstream connection entirely (no redundant path)
- The Inn, Marketing, THCC go dark
- Warehouse, Nordic Center, FarmHouse go dark
- Base village operations: ticketing, rentals, ski school check-in, patrol dispatch — all degraded or offline

**Revenue impact:**
- Base village is where guests check in, rent gear, and buy lift tickets
- If POS systems go down: ticket sales halt, rental operations manual
- Estimated guest throughput delay: 30–60 min per guest at peak
- With 5,000+ guests, this creates a cascading check-in failure

**Daily impact estimate:** $200k–$600k (indirect — lost throughput, refunds, guest experience)
**Reputational impact:** High — this is the guest-facing layer

> **⚠️ Leased segment additional risk:** Unlike owned infrastructure, Vail cannot dispatch their own crew to repair a leased segment. Restoration depends on the lessor's SLA. If no SLA exists, restoration time is entirely at the vendor's discretion.

### Recommendations — Resilience

1. **Harden the MOC → Spruce Camp corridor** — add a second buried 12 SM run on a physically separate path (different conduit, different trench route). Estimated cost: $50k–$120k. This eliminates the single most consequential single point of failure.

2. **Establish an emergency SLA with the leased segment vendor** — minimum 4-hour restoration guarantee for the SML → Admin run. Negotiate now, before a failure occurs.

3. **Pre-stage emergency fiber splice kits** at MOC and Spruce Camp. A field splice can restore connectivity in 2–4 hours vs. 24+ hours waiting for a vendor. Kit cost: ~$3,000–$5,000.

4. **Document the Over Easy lift fiber path** as the formal failover route for the MOC → Spruce Camp segment. Test it under load at least once per season during a low-traffic window.

5. **Tag the defunct 6-strand MM run (MOC → Mansfield)** for removal or repurposing. It represents a liability (physical clutter, potential confusion during an incident) with no current value.

6. **Verify F.A.A.T Building identity and snowmaking dependency.** If confirmed as a snowmaking hub, its 60-strand uplink from Spruce Camp should have a dedicated protection plan given the revenue implications of snowmaking outages.

---

## Summary Score Card

| Issue | Severity | Recommended Action | Timeline |
|-------|----------|--------------------|----------|
| Leased SML→Admin — no redundancy | 🔴 Critical | Emergency SLA + budget for owned replacement study | This quarter |
| MOC→Spruce Camp single path | 🔴 Critical | Second buried run, separate route | Capital plan FY27 |
| F.A.A.T identity unconfirmed | 🟡 Medium | Field verification with Ryan K. | Next week |
| No pre-staged splice kits | 🟡 Medium | Purchase and stage at MOC + Spruce Camp | Immediate |
| Defunct MM run not decommissioned | 🟢 Low | Remove / document in asset registry | Off-season |
| Estimated elevations (not LiDAR) | 🟢 Low | Run stage2a_dem.py locally | Next sprint |
