sequenceDiagram
title SEQ-1: Plan Rectangular Mission and Export to OpenPass

participant FieldOperator
participant PathPlannerModule
participant EdgeDatabase
participant EdgeFileStore
participant OpenPass

FieldOperator->>PathPlannerModule: Define plot boundary (coords/dimensions) [US-01, FR-1]
PathPlannerModule->>PathPlannerModule: Validate inputs and camera/flight params [US-02]
PathPlannerModule->>EdgeDatabase: Save mission template and parameters
EdgeDatabase-->>PathPlannerModule: MissionId

FieldOperator->>PathPlannerModule: Request waypoint plan generation [US-03, UC1]
PathPlannerModule->>PathPlannerModule: Compute rectangular grid, overlaps, FOV [FR-2]
PathPlannerModule->>EdgeFileStore: Write mission manifest (version=1) [FR-3]
PathPlannerModule->>EdgeDatabase: Store coverage + image count estimates [FR-12]
EdgeDatabase-->>PathPlannerModule: Ack

FieldOperator->>PathPlannerModule: Preview mission layout [US-04]
PathPlannerModule-->>FieldOperator: Rendered preview / summary

alt Export accepted
  FieldOperator->>PathPlannerModule: Export mission to OpenPass [US-05]
  PathPlannerModule->>OpenPass: Send manifest file path / payload (missionId, schemaVersion)
  OpenPass-->>PathPlannerModule: Manifest validation result
  PathPlannerModule-->>FieldOperator: "Mission exported successfully"
else Invalid parameters or export failure
  OpenPass-->>PathPlannerModule: Error (invalid schema / parameters)
  PathPlannerModule->>EdgeDatabase: Mark mission as invalid + reason
  PathPlannerModule-->>FieldOperator: Error message and suggested fixes
end


sequenceDiagram
title SEQ-2: Image Detection, Batching, and Resumable Upload

participant Drone
participant EdgeFileStore
participant TransferModule
participant EdgeDatabase
participant TapisAPI
participant HPCCluster

Drone->>EdgeFileStore: Write new image files into mission folder
loop Watch mission folder [FR-4]
  TransferModule->>EdgeFileStore: Scan for new files since last checkpoint [US-10]
  EdgeFileStore-->>TransferModule: List of new image paths
  TransferModule->>EdgeDatabase: Persist file records (hash, size, missionId) [FR-8]
  EdgeDatabase-->>TransferModule: Ack
end

loop Build batches [FR-5, ADR-004]
  TransferModule->>TransferModule: Group images by size/time thresholds (batchId)
  TransferModule->>EdgeDatabase: Create UploadSession(sessionId, batchId, status=PENDING)
  EdgeDatabase-->>TransferModule: Ack
end

TransferModule->>TransferModule: Compute checksums and validate batch [FR-10]
alt Batch passes integrity and storage checks
  TransferModule->>TapisAPI: POST /files/upload (sessionId, batchId, checksum) over HTTPS [FR-6]
  alt Network OK
    TapisAPI->>HPCCluster: Store images in project storage
    TapisAPI-->>TransferModule: Upload success + remotePath
    TransferModule->>EdgeDatabase: Mark UploadSession COMPLETED
  else Network error / interruption
    TapisAPI-->>TransferModule: Error (timeout/connection drop)
    TransferModule->>EdgeDatabase: Record failure, retryCount++, lastError [FR-9]
    loop Retry with exponential backoff [NFR-REL-001]
      TransferModule->>TapisAPI: Retry upload (sessionId, batchId, offset) [FR-6, FR-11]
      TapisAPI-->>TransferModule: Success or failure
    end
  end
else Integrity or deduplication failure
  TransferModule->>EdgeDatabase: Mark UploadSession FAILED (reason=INTEGRITY/DEDUP) [FR-8, FR-10]
  TransferModule-->>EdgeFileStore: Optionally quarantine bad files
end


sequenceDiagram
title SEQ-3: Trigger ML Job and Monitor Completion

participant FieldOperator
participant TransferModule
participant EdgeDatabase
participant TapisAPI
participant HPCCluster

TransferModule->>EdgeDatabase: Query for completed UploadSessions without jobs [FR-7]
EdgeDatabase-->>TransferModule: List of eligible sessions

loop For each eligible session
  TransferModule->>TapisAPI: POST /jobs/submit (sessionId, jobTemplateId, idempotencyKey) [FR-7]
  TapisAPI->>HPCCluster: Start ML job for uploaded batch
  TapisAPI-->>TransferModule: jobId, accepted
  TransferModule->>EdgeDatabase: Persist jobId, status=SUBMITTED
end

par Periodic status polling
  loop Until job completes or times out
    TransferModule->>TapisAPI: GET /jobs/{jobId}/status
    TapisAPI-->>TransferModule: Status (RUNNING/FAILED/SUCCEEDED)
    TransferModule->>EdgeDatabase: Update job status and timestamps
  end
and Operator status view
  FieldOperator->>TransferModule: Request transfer + job status [US-08, US-09]
  TransferModule->>EdgeDatabase: Fetch mission, upload, and job summaries
  EdgeDatabase-->>TransferModule: Status snapshot
  TransferModule-->>FieldOperator: Human-readable status (per mission)
end

alt Job succeeded
  HPCCluster-->>TapisAPI: Final job state + result locations
  TapisAPI-->>TransferModule: SUCCEEDED, outputsPath
  TransferModule->>EdgeDatabase: Store outputsPath, metrics, completion time [FR-12]
  TransferModule-->>FieldOperator: "Job completed" in UI/CLI [US-09]
else Job failed or timed out
  TapisAPI-->>TransferModule: FAILED or TIMEOUT
  TransferModule->>EdgeDatabase: Record failure reason and recommendation
  TransferModule-->>FieldOperator: Error + guidance, with option to retry job safely
end
