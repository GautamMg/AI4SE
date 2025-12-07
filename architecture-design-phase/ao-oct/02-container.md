# C4: Container

```mermaid
graph LR
  subgraph AO-OCT-MAS
    UI[Web UI\nType: SPA\nResp: Case view, review, edits, model UI]
    API[API Gateway\nType: REST/gRPC\nResp: AuthN/Z, routing, rate limit]
    PIPE[Pipeline Orchestrator\nType: Workflow engine\nResp: Runs, manifests, retries, idempotency]
    ENG[Analytics Engine\nType: GPU services\nResp: Preproc, registration, segmentation, metrics]
    MR[Model Registry & Serving\nType: Registry+Serving\nResp: Model cards, versions, canary/shadow]
    MDB[(Metadata DB\nType: Postgres\nResp: Cases, runs, labels, configs, audits index)]
    OBJ[(Object Storage\nType: S3-compatible\nResp: Volumes, masks, overlays, manifests)]
    AUD[Audit & Monitoring\nType: Logs+Metrics\nResp: Access logs, traces, drift stats)]
  end

  SSO[SSO / IdP]
  PACS[PACS / AO-OCT Devices]
  RS[Research Storage / Shares]
  HIS[Hospital Systems / HL7/DICOM SR]

  UI -->|HTTPS + OIDC tokens| API
  API -->|OIDC/SAML| SSO

  PACS -->|DICOM C-STORE / secure file drop| API

  API -->|REST /cases,/runs,/labels,/models| PIPE
  API -->|REST/GraphQL| MR
  API -->|REST metrics/manifests| MDB
  API -->|Presigned URLs| OBJ

  PIPE -->|gRPC/REST tasks| ENG
  PIPE -->|Insert RUN manifests| MDB
  PIPE -->|Write artifacts| OBJ
  PIPE -->|Emit events/logs| AUD

  ENG -->|Read inputs / write outputs| OBJ
  ENG -->|Update QC, metrics, status| MDB
  ENG -->|Fetch models| MR

  MR -->|Store metadata| MDB
  MR -->|Store weights URI| OBJ

  AUD -->|Ingest logs, traces| API
  AUD -->|Store audits index| MDB

  API -->|Scheduled REST/S3 exports| RS
  API -->|HL7/DICOM SR metrics| HIS
```

*Caption: Eight containers with explicit protocols and responsibilities aligned to FR/NFR.*
