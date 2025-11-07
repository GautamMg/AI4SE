# AO-OCT-MAS — INVEST-Checked User Stories

> Legend: Traces map to SRS IDs (FR-xxx / NFR-xxx / U-/A-/D-/F-).

## Stories

1. **Researcher** uploads an AO-OCT volume and gets a RUN_ID to track processing.  
   **AC:** `POST /cases`, then `POST /runs` returns 202 + RUN_ID; `GET /runs/{id}` shows QUEUED→RUNNING→SUCCEEDED/FAILED.  
   **Trace:** FR-001, FR-002, FR-004, A-01..A-04

2. **Imaging Tech** gets automatic motion correction with a QC score to reject poor scans.  
   **AC:** Preproc emits QC∈[0,1]; runs with QC<0.4 auto-flagged.  
   **Trace:** FR-010, FR-041

3. **Clinician** views cone density maps with uncertainty to judge reliability.  
   **AC:** Output includes density map and uncertainty; UI displays both with legend.  
   **Trace:** FR-030, FR-033, FR-040, U-01

4. **Researcher** exports capillary diameter stats per ROI to compare cohorts.  
   **AC:** CSV/Parquet export contains per-ROI mean, median, std, CI.  
   **Trace:** FR-031, FR-040, FR-080

5. **Labeler** edits a mask and saves versions so corrections are auditable.  
   **AC:** Edit creates new LABEL_ID with diff; rollback possible; audit log updated.  
   **Trace:** FR-050, FR-071, U-02

6. **Labeler** receives active-learning tiles to focus on low-confidence areas.  
   **AC:** Queue shows tiles ranked by uncertainty > threshold; click opens editor.  
   **Trace:** FR-051, FR-033, U-02

7. **ML Engineer** registers a model with a card so promotion is controlled.  
   **AC:** `POST /models` stores weights, metrics, data hash, risks; card visible in UI.  
   **Trace:** FR-060, U-03, A-06

8. **ML Engineer** runs canary deploys to test a candidate safely.  
   **AC:** Shadow traffic supported; promotion requires metric gates; rollback one click.  
   **Trace:** FR-061, NFR-R-01

9. **Admin** uses SSO + RBAC so only authorized users access PHI.  
   **AC:** Login via SSO; roles restrict endpoints; failed access logged.  
   **Trace:** FR-070, FR-071, NFR-S-01

10. **Researcher** downloads a full provenance manifest so results are reproducible.  
    **AC:** Manifest lists input checksums, code commit, model id, params, seeds, container digests, GPU info.  
    **Trace:** FR-003, FR-004

11. **Clinician** toggles overlays to verify masks against raw data.  
    **AC:** UI toggles raw/mask/uncertainty; pan/zoom; <100 ms tile latency.  
    **Trace:** U-01, NFR-U-01

12. **Data Manager** applies PHI de-identification so exports are safe.  
    **AC:** Exports contain no PHI; logs redact PHI fields; compliance test passes.  
    **Trace:** FR-072, FR-080, NFR-S-02

13. **ML Engineer** receives drift alerts to retrain proactively.  
    **AC:** Weekly job compares population stats and ECE; alert if thresholds exceeded.  
    **Trace:** FR-062, NFR-O-01

14. **PI** schedules cohort exports so analysts get fresh data.  
    **AC:** Time-based exports to S3 path with manifest and metrics; checksum verified.  
    **Trace:** FR-080, FR-004

15. **QA** runs a golden-case suite so regressions are blocked.  
    **AC:** CI executes acceptance tests tied to RTM; failures block merge.  
    **Trace:** VV-01, VV-02, NFR-M-01

16. **Reviewer** conducts multi-rater adjudication so final labels reflect consensus.  
    **AC:** Two independent edits required; adjudicator resolves; provenance stored.  
    **Trace:** FR-052, FR-071

17. **Operator** gets retries and idempotent runs so transient errors don’t duplicate outputs.  
    **AC:** Re-posting same RUN spec returns same RUN_ID; at-least-once processing without duplicates.  
    **Trace:** NFR-R-01, FR-004

18. **Auditor** exports access logs so compliance checks are possible.  
    **AC:** Exportable audit trail for any case within a date range.  
    **Trace:** FR-071, NFR-O-01

---

## INVEST Check
- **Independent:** No hard dependencies between stories.  
- **Negotiable:** Scope refined via AC and traces.  
- **Valuable:** Each delivers measurable value to a user role.  
- **Estimable:** Clear AC and system boundaries.  
- **Small:** Fit within a sprint.  
- **Testable:** AC linked to SRS enable objective tests.
