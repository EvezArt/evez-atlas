# Undiscovered Proof — Starter Pack

This repository is a field-ready scaffold to correlate **money, movement, sensors, and documents** over two initial Areas of Interest (AOIs):

- AOI_Laughlin_DavisDam_PyramidCanyon (NV/AZ)
- AOI_Fort_Huachuca_Sierra_Vista (AZ)

**Date window:** 2023-01-01 → 2025-08-02 (adjust in `config/config.yaml`).

## Modules
- ETL pipelines for USAspending, FEC, FCC ASR/ULS, OpenSky/AIS, Sentinel-1 (via ASF HyP3), and NASA Black Marble.
- Analytics scoring to triage 1 km tiles by multi-modal convergence.
- FOIA drafts for DOI (Davis Dam region) and Department of the Army (Fort Huachuca) requesting contracts, SOWs, model inventories, and change logs.
- Cypher queries to surface convergence nodes in Neo4j.

**Lawful collection only.** These tools are designed for open data and metadata; do not intercept content or bypass controls.
