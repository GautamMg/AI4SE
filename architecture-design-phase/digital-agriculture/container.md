C4Container
title Aerial Data Automation System - Container View

Person(FieldOperator, "Field Operator / Researcher", "Uses CLI/UX to plan missions and monitor transfers.")

System_Boundary(AerialSystem, "Aerial Data Automation System") {

  Container(PathPlannerModule, "Path Planner Module (PPM)", "Python CLI/Service",
    "Generates rectangular waypoint grids and OpenPass-compatible mission manifests from plot and camera parameters. [FR-1..FR-3, US-01..US-05]")

  Container(TransferModule, "Transfer Module (TM)", "Python Daemon/Service",
    "Monitors mission folder, batches new images, performs resumable uploads, triggers ML jobs, and tracks status. [FR-4..FR-8, FR-10..FR-12, US-08..US-16]")

  ContainerDb(EdgeDatabase, "Edge Database", "SQLite",
    "Persists missions, templates, upload sessions, dedup hashes, and HPC job status. [FR-8, FR-11, FR-12, NFR-REL-001, NFR-REL-002]")

  Container(EdgeFileStore, "Edge File Store", "Local filesystem",
    "Stores mission manifests and locally captured image batches within a configured mission folder. [FR-4, FR-5, FR-10, NFR-PORT-001]")
}

System_Ext(OpenPass, "OpenPass Mission Control", "Executes missions based on manifest files.")
System_Ext(Drone, "Parrot Anafi Drone", "Captures images and writes them into the mission output folder.")
System_Ext(TapisAPI, "Tapis API", "File-transfer and job API to HPC.")
System_Ext(HPCCluster, "HPC Cluster (OSC)", "Computes ML training/inference jobs.")

Rel(FieldOperator, PathPlannerModule, "Provide plot and flight parameters via CLI/UI [US-01, US-02]")
Rel(FieldOperator, TransferModule, "Configure transfer settings and inspect status/logs [US-08, US-09]")

Rel(PathPlannerModule, EdgeDatabase, "Create/update mission records and templates")
Rel(PathPlannerModule, EdgeFileStore, "Write mission manifests and preview artifacts")
Rel(PathPlannerModule, OpenPass, "Export mission manifest (file/API) [FR-3, US-05]")

Rel(Drone, EdgeFileStore, "Write captured images into mission folder")
Rel(TransferModule, EdgeFileStore, "Watch folder, detect new images, build batches [FR-4, FR-5]")

Rel(TransferModule, EdgeDatabase, "Persist transfer sessions, batch metadata, dedup hashes, job status [FR-8, FR-11, FR-12]")
Rel(TransferModule, TapisAPI, "Upload batches, submit and poll jobs via REST/HTTPS [FR-6, FR-7, FR-10, NFR-SEC-001]")
Rel(TapisAPI, HPCCluster, "Deliver files and start ML pipeline jobs")
