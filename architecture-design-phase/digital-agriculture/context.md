C4Context
title Aerial Data Automation System - System Context

Person(FieldOperator, "Field Operator / Researcher", "Plans missions and monitors data transfers and HPC jobs.")
System(AerialSystem, "Aerial Data Automation System", "Edge software for path planning and data transfer automation.")
System_Ext(OpenPass, "OpenPass Mission Control", "Executes waypoint missions on the drone.")
System_Ext(Drone, "Parrot Anafi Drone", "Captures images along the mission path.")
System_Ext(TapisAPI, "Tapis API", "Managed file-transfer and job-submission interface to the HPC cluster.")
System_Ext(HPCCluster, "HPC Cluster (OSC)", "Runs ML training/inference jobs and stores results.")

Rel(FieldOperator, AerialSystem, "Define plots, set parameters, monitor transfers and jobs [US-01..US-09]")
Rel(AerialSystem, OpenPass, "Export rectangular waypoint mission manifests [FR-3, US-05]")
Rel(OpenPass, Drone, "Control flight, capture images to mission folder")
Rel(AerialSystem, TapisAPI, "Upload image batches, submit/query ML jobs over HTTPS [FR-6, FR-7]")
Rel(TapisAPI, HPCCluster, "Store images and execute jobs")
