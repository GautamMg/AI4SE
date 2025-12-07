# C4: System Context

```mermaid
graph LR
  subgraph AO-OCT-MAS [AO-OCT Microstructure Analytics System]
    UI[Web UI]
    API[API Gateway]
    PIPE[Pipeline Orchestrator]
    ENG[Analytics Engine]
    MR[Model Registry & Serving]
    MDB[(Metadata DB)]
    OBJ[(Object Storage)]
    AUD[Audit & Monitoring]
  end

  VR[Vision Researcher]
  RC[Retinal Clinician]
  IT[Imaging Technician]
  LB[Labeler / Adjudicator]
  MLE[ML Engineer]
  ADMN[Admin]
  QA_ACT[QA]
  AUD_ACT[Auditor]
  PI_ACT[PI]
  DM[Data Manager]
  OP[Operator]

  SSO[SSO / IdP]
  PACS[PACS / AO-OCT Devices]
  RS[Research Storage / Shares]
  HIS[Hospital Systems / HL7-Destinations]

  VR -->|Review metrics, overlays| UI
  RC -->|Clinical review of maps & metrics| UI
  IT -->|Monitor runs, re-queue jobs| UI
  LB -->|Edit masks, adjudicate| UI
  MLE -->|Manage models & runs| UI
  ADMN -->|Manage RBAC, config| UI
  QA_ACT -->|Golden-case, RTM checks| UI
  AUD_ACT -->|Access logs, compliance views| UI
  PI_ACT -->|Cohort exports| UI
  DM -->|De-ID, retention checks| UI
  OP -->|Ops, retries| UI

  UI -->|REST/gRPC API calls| API
  API -->|Submit runs, query status| PIPE
  PIPE -->|Invoke processing stages| ENG
  ENG -->|Read/write metrics & manifests| MDB
  ENG -->|Store volumes, masks, overlays| OBJ
  MR -->|Expose model cards & versions| UI
  PIPE -->|Use models for inference| MR
  AUD -->|Collect logs, traces, audits| MDB

  UI -->|SSO Auth (OIDC/SAML)| SSO
  PACS -->|DICOM C-STORE / file drops| API
  API -->|De-identified exports| RS
  API -->|Metrics-only HL7/DICOM SR| HIS
```

*Caption: AO-OCT-MAS as secure, auditable hub between users, devices, and external systems.*
