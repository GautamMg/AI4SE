# AO-OCT Microstructure Analytics System (AO-OCT-MAS) — SRS

## 1. Introduction
### 1.1 Purpose
Specify functional and non-functional requirements for the AO-OCT Microstructure Analytics System (AO-OCT-MAS).

### 1.2 Scope
From data ingest to validated metrics and export. Acquisition hardware is out of scope; adapters integrate with scanners/PACS.

### 1.3 Definitions
- **AO-OCT**: Adaptive Optics Optical Coherence Tomography  
- **ROI**: Region of interest  
- **PHI/PII**: Protected/Personally identifiable information  
- **Provenance**: Lineage of data, code, model, params, and outputs

### 1.4 References
Project policies, HIPAA Security Rule, internal data governance SOPs.

### 1.5 Overview
Actors, interfaces, system features, constraints, data, quality, verification.

---

## 2. Overall Description
### 2.1 Product Perspective
Modular pipeline with containers for ingest, preprocessing, registration, segmentation, metrics, review UI, and export. Object storage, metadata DB, model registry.

### 2.2 User Classes
- Clinician/Researcher: reads metrics, reviews overlays
- Imaging Tech: monitors runs, re-queues failed jobs
- Labeler/Adjudicator: edits masks
- ML Engineer: trains models, promotes versions
- Admin: manages access and audit

### 2.3 Operating Environment
Linux, CUDA GPUs, Kubernetes or Docker Compose; Postgres; S3-compatible storage; REST/gRPC; optional DICOM.

### 2.4 Constraints
- **C-01** PHI never written to non-approved storage
- **C-02** All outputs tied to immutable run manifest
- **C-03** Deterministic seeds for training/inference unless flagged

### 2.5 Assumptions
Volumes include voxel size metadata; device calibration files available; IRB approvals in place.

### 2.6 Dependencies
CUDA, PyTorch/TensorRT, IT policies, SSO provider.

---

## 3. External Interface Requirements
### 3.1 User Interfaces
- **U-01** Web UI to upload/view cases, overlays, metrics
- **U-02** Review tool for mask edits with versioning and comments
- **U-03** Model registry UI with metrics and promotion gates

### 3.2 APIs
- **A-01** `POST /cases` register a case + metadata
- **A-02** `POST /runs` trigger pipeline; returns RUN_ID
- **A-03** `GET /runs/{id}` status, artifacts, logs
- **A-04** `GET /cases/{id}/metrics` metrics bundle
- **A-05** `POST /labels` submit edits; provenance recorded
- **A-06** `GET /models/{id}` model card + metrics

### 3.3 Hardware/Device Interfaces
- **D-01** DICOM C-STORE listener (optional)
- **D-02** File drop watcher for OCT-BIN, TIFF, NIfTI via S3/NFS

### 3.4 Data Formats
- **F-01 Inputs**: DICOM, OCT-BIN, TIFF stacks, NIfTI; JSON sidecars  
- **F-02 Outputs**: NIfTI masks, PNG overlays, Parquet/CSV metrics, JSON manifests

---

## 4. System Features (Functional Requirements)

### 4.1 Ingestion & Provenance
- **FR-001** Register case with device metadata and de-ID policy  
- **FR-002** Validate and convert input to internal voxel grid; reject on missing scale  
- **FR-003** Create immutable RUN manifest: input checksums, code refs, model IDs, params, seeds, container digests, hardware  
- **FR-004** Store artifacts in versioned object storage and index in DB

### 4.2 Preprocessing
- **FR-010** Motion correction and volume stabilization with QC score  
- **FR-011** Speckle reduction configurable by tissue; log PSNR/SSIM deltas  
- **FR-012** Illumination/tilt normalization; retain pre/post snapshots

### 4.3 Registration & Layering
- **FR-020** Segment canonical retinal layers; align ROIs; export transforms

### 4.4 Segmentation
- **FR-030** Cones: instance or centroid map; output density/spacing maps  
- **FR-031** Capillaries: segment lumen; output diameter and flow proxies  
- **FR-032** Nerve fiber bundles: delineate bundles and thickness  
- **FR-033** Emit per-structure uncertainty maps

### 4.5 Quantification
- **FR-040** Compute metrics per ROI: densities, spacing, diameters, thickness, coverage, uncertainty  
- **FR-041** Export metrics with confidence intervals and QC flags

### 4.6 Human-in-the-Loop
- **FR-050** Review UI to accept/edit masks; diff and rollback  
- **FR-051** Active-learning queue: sample high-uncertainty or low-agreement tiles  
- **FR-052** Adjudication workflow with multi-rater consensus

### 4.7 Model Lifecycle
- **FR-060** Register models with cards: data, training config, metrics, risks  
- **FR-061** Canary and shadow deployments; promotion gates by metric thresholds  
- **FR-062** Drift detection via population stats and calibration error

### 4.8 Security, Audit, Compliance
- **FR-070** SSO + RBAC; least privilege on APIs and buckets  
- **FR-071** Full audit log of data access, edits, exports  
- **FR-072** PHI encryption at rest and in transit; field-level de-ID

### 4.9 Integration & Export
- **FR-080** REST/Parquet exports; scheduled drops to research shares  
- **FR-081** Optional HL7/DICOM SR export of metrics without PHI

---

## 5. Non-Functional Requirements

### Performance
- **NFR-P-01** Inference throughput ≥ 10 volumes/hour/GPU for 512×512×N  
- **NFR-P-02** Preproc+registration < 3 min/volume p95

### Reliability/Availability
- **NFR-R-01** Automated retry with idempotent runs  
- **NFR-R-02** MTTR < 30 min for pipeline failures

### Accuracy/Robustness
- **NFR-A-01** Dice/F1 ≥ 0.90 cones, ≥ 0.88 capillaries on internal test  
- **NFR-A-02** Cross-site drop ≤ 5 points; calibration ECE ≤ 0.05

### Security/Privacy
- **NFR-S-01** All buckets KMS-encrypted; TLS 1.2+  
- **NFR-S-02** No raw PHI in logs; redaction filters mandatory

### Usability
- **NFR-U-01** Reviewer can edit a 512×512 tile with ≤ 100 ms latency

### Maintainability/Portability
- **NFR-M-01** > 80% pipeline code unit-tested; CI green gate  
- **NFR-M-02** All components containerized; deployable on k8s and Docker Compose

### Observability
- **NFR-O-01** Traces for every run; metrics and logs with 30-day retention

---

## 6. Data Requirements
- **DR-01** Dataset catalog with license, consent, and device metadata  
- **DR-02** Ground truth stored as versioned masks with rater IDs  
- **DR-03** Retention: raw 1 year, derived 3 years, manifests 7 years  
- **DR-04** Synthetic data generation recipes for privacy-preserving tests

---

## 7. Verification & Validation
- **VV-01** Requirement-to-test traceability matrix (RTM) covers all FR/NFR  
- **VV-02** Golden-case regression suite runs on each model promotion  
- **VV-03** Reader-study protocol compares model vs expert for key metrics  
- **VV-04** Adversarial/robustness tests: noise, blur, tilt, missing slices

---

## 8. Appendices
Glossary, risk register, SOP links, model cards template.
