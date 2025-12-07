# Architecture Decision Records (ADRs)

## ADR-01: Pipeline Orchestration via Containerized Workflow Engine

- Context: Need reproducible runs, retries, manifests, isolation.  
  - SRS: 2.1, 4.1, 4.5, 5 (NFR-R-01, NFR-M-02).  
  - Stories: S01 (upload+RUN_ID), S17 (retries/idempotent), S10 (provenance).  
- Options:
  - A: Monolith handles ingest, processing, metrics.
  - B: External workflow engine (Argo/Airflow-style) + per-stage containers.
- Trade-offs:
  - A: Simpler; weak provenance; limited scaling; harder retries.
  - B: More ops; clear DAGs; better scalability; strong traceability.
- Decision: Choose B. Use `Pipeline Orchestrator` (PIPE) to manage runs and steps.
- Revisit: If load stays trivial or engine overhead dominates.
- Links: C4 Containers (PIPE, ENG, MDB, OBJ, AUD); Seq-1; NFR-R-01; NFR-M-02.

## ADR-02: Imaging Data in Object Storage, Metadata in RDBMS

- Context: Large AO-OCT volumes, versioning, exports, retention.  
  - SRS: 2.1, 3.4, 4.1, 6 (DR-01..DR-03).  
  - Stories: S01, S04, S14, S18.
- Options:
  - A: Store binaries and metadata in Postgres.
  - B: Store binaries in S3-compatible OBJ, metadata in Postgres MDB.
- Trade-offs:
  - A: Simple; poor scalability; heavy backups.
  - B: Scales; cheap; supports immutable manifests; needs referential discipline.
- Decision: Choose B. OBJ for volumes/masks/overlays/manifests; MDB for indexes.
- Revisit: If platform lacks reliable object store.
- Links: C4 (OBJ, MDB); Seq-1; STRIDE storage rows.

## ADR-03: Immutable RUN Manifests for Provenance

- Context: Regulatory, reproducibility, audits.  
  - SRS: 1.3, 4.1 (FR-003, FR-004), 7 (VV-01..VV-03).  
  - Stories: S10 (provenance), S18 (audit).
- Options:
  - A: Best-effort logging across services.
  - B: Required manifest per RUN with full lineage.
- Trade-offs:
  - A: Gaps; weak evidence; hard RTM.
  - B: Slight overhead; strong lineage; simple audits.
- Decision: Choose B. PIPE/ENG write manifest in OBJ; MDB stores pointer.
- Revisit: If storage or latency forces manifest compaction.
- Links: C4 (PIPE, ENG, MDB, OBJ, AUD); Seq-1; STRIDE repudiation mitigation.

## ADR-04: Single Web UI with Role-Based Views

- Context: Human-in-the-loop review, adjudication, model governance.  
  - SRS: 3.1 (U-01..U-03), 4.6, 4.7, 5 (NFR-U-01).  
  - Stories: S03, S05, S06, S11, S16.
- Options:
  - A: Multiple specialized UIs.
  - B: One UI with RBAC-scoped capabilities.
- Trade-offs:
  - A: Tailored; fragmented; harder governance.
  - B: Unified; simpler RBAC/audit; needs clear UX separation.
- Decision: Choose B. `Web UI` as single entrypoint.
- Revisit: If scale or security isolation needs separate apps.
- Links: C4 (UI, API); Seq-2; STRIDE spoofing.

## ADR-05: Mandatory SSO + RBAC for All Access

- Context: PHI, compliance, least privilege.  
  - SRS: 2.4, 4.8 (FR-070..FR-072), 5 (NFR-S-01, NFR-S-02).  
  - Stories: S09 (SSO+RBAC), S18 (audits), S12 (de-ID).
- Options:
  - A: Local accounts in AO-OCT-MAS.
  - B: Institutional SSO with role mapping and central logs.
- Trade-offs:
  - A: Fast; non-compliant; scattered identities.
  - B: Integration effort; strong security; unified control.
- Decision: Choose B. API/UI trust only SSO-issued tokens; enforce RBAC centrally.
- Revisit: If offline deployments require pluggable IdP.
- Links: C4 edges to SSO; STRIDE spoofing/elevation; all sequences.
