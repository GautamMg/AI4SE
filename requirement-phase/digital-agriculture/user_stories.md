# Aerial Data Automation — User Stories (ChatGPT)

Automate aerial data collection and transfer from Parrot Anafi drones to HPC systems (e.g., OSC) using Path Planner and Transfer Modules.  
This document captures user stories grouped by key personas and system roles.

---

## 1. Field Operator / Researcher

| ID     | Title                   | User Story                                                                                                                                                         |
|--------|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| US-01  | Define Field Boundary   | As a field operator, I want to draw or input rectangular field coordinates, so that I can define the area for drone data collection.                               |
| US-02  | Set Flight Parameters   | As a field operator, I want to specify flight height, overlap, and camera parameters, so that I can ensure image coverage meets analysis requirements.            |
| US-03  | Generate Waypoint Plan  | As a field operator, I want the system to automatically generate a rectangular waypoint plan, so that I don’t have to manually calculate flight paths.           |
| US-04  | Preview Mission Layout  | As a field operator, I want to visualize the generated waypoint path on a map, so that I can confirm the coverage before the drone flight.                       |
| US-05  | Export Mission to Drone | As a field operator, I want to export the generated waypoint file in a format compatible with OpenPass, so that the mission can be executed on the Parrot Anafi. |
| US-06  | Save Mission Template   | As a field operator, I want to save and reuse flight templates, so that I can perform repeat flights over the same field efficiently.                             |
| US-07  | Offline Mission Support | As a field operator, I want to run flight planning tools offline, so that I can plan missions in areas with no network connectivity.                              |
| US-08  | View Transfer Progress  | As a field operator, I want to monitor the upload progress of collected images, so that I know when data transfer to the HPC system is complete.                 |
| US-09  | Receive Job Completion Updates | As a field operator, I want to receive notifications once my images have been processed (training or inference completed), so that I can review results promptly. |

---

## 2. System (Automation Engine / Edge Service)

| ID     | Title                      | User Story                                                                                                                                              |
|--------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| US-10  | Auto-Detect New Images     | As the system, I want to monitor the drone’s mission folder, so that I can detect and process newly captured images automatically.                      |
| US-11  | Batch Uploads              | As the system, I want to batch images into groups based on size or time intervals, so that uploads are optimized for limited connectivity.              |
| US-12  | Retry Failed Transfers     | As the system, I want to retry uploads automatically when the network is unstable, so that data transfer eventually completes successfully.            |
| US-13  | Resume Interrupted Transfers | As the system, I want to resume from partially uploaded batches, so that I avoid re-uploading large files unnecessarily.                               |
| US-14  | Deduplicate Data           | As the system, I want to detect already uploaded images, so that I can skip redundant uploads and save bandwidth.                                      |
| US-15  | Validate Data Quality      | As the system, I want to perform basic checks (e.g., image corruption, file size) before uploading, so that only valid data is sent to HPC.           |
| US-16  | Manage Local Storage       | As the system, I want to delete or compress old image batches after upload confirmation, so that I can free up local disk space.                       |
| US-17  | Trigger HPC Jobs           | As the system, I want to initiate predefined HPC workflows (training/inference) upon successful upload, so that downstream processing begins automatically. |
| US-18  | Handle Low Connectivity    | As the system, I want to queue transfers when offline and resume when connectivity returns, so that no data is lost.                                   |
| US-19  | Log and Audit Operations   | As the system, I want to maintain detailed logs of uploads, retries, and job triggers, so that administrators can review system behavior later.        |

---

## 3. Administrator / System Maintainer

| ID     | Title                     | User Story                                                                                                                                           |
|--------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| US-20  | Configure HPC Credentials | As an administrator, I want to configure and update Tapis or HPC authentication tokens, so that data transfers and job triggers remain authorized.  |
| US-21  | Set Network Parameters    | As an administrator, I want to configure retry intervals, batch sizes, and bandwidth limits, so that transfers can adapt to varying field conditions.|
| US-22  | Monitor System Health     | As an administrator, I want to view real-time metrics of transfers, storage, and job statuses, so that I can detect failures or bottlenecks.        |
| US-23  | Manage Job Templates      | As an administrator, I want to define and edit job templates for HPC workflows (e.g., inference, retraining), so that edge devices can trigger standardized tasks. |
| US-24  | Audit Logs                | As an administrator, I want to review historical logs and transfer records, so that I can ensure compliance and troubleshoot issues.                |
| US-25  | Update Software Modules   | As an administrator, I want to remotely update the path planner or transfer modules, so that all devices stay synchronized with the latest version. |

---

## 4. Developer / Integrator

| ID     | Title                        | User Story                                                                                                                                          |
|--------|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| US-26  | API Access for Mission Creation | As a developer, I want an API endpoint to generate waypoint plans from given coordinates, so that I can integrate this functionality into external systems. |
| US-27  | API for Transfer Trigger     | As a developer, I want an endpoint to manually trigger a file transfer or HPC job, so that other automation systems can interface with this service. |
| US-28  | Plugin Architecture          | As a developer, I want to extend the transfer logic using a plugin system, so that new protocols (e.g., S3, Globus) can be supported easily.        |
| US-29  | Error Handling Hooks         | As a developer, I want callback hooks for failure events, so that I can integrate alerting or fallback recovery mechanisms.                         |

---

## 5. Future / Extended Features

| ID     | Title                    | User Story                                                                                                                                          |
|--------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| US-30  | Adaptive Flight Planning | As a field operator, I want the planner to adjust waypoints based on wind or battery limits, so that missions can complete safely and efficiently. |
| US-31  | Multi-Drone Coordination | As a researcher, I want to plan coordinated missions for multiple drones, so that I can cover larger areas in parallel.                            |
| US-32  | Edge AI Pre-filtering    | As the system, I want to filter out blank or low-value images locally, so that only meaningful data is transferred.                               |
| US-33  | Automated Reporting      | As an administrator, I want the system to generate daily mission and transfer reports, so that stakeholders can track overall progress.           |
