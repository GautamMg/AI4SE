# Software Requirements Specification (SRS)

## 1. Document Control

- **Title**: SRS – Aerial Data Collection & Transfer Automation System  
- **Version**: 1.0  
- **Date**: October 19, 2025  
- **Author**: ChatGPT, on behalf of Harikesh Byrandurga Gopinath  

---

## 2. Introduction

### 2.1 Purpose

This document defines the functional and non-functional requirements for a system that automates aerial data collection using Parrot Anafi drones and streamlines the transfer of captured imagery from field devices to high-performance computing (HPC) environments. The goal is to minimize manual intervention, ensure efficient mission planning, and trigger downstream ML workflows automatically and reliably.

### 2.2 Scope

The system comprises two main components:

- **Path Planner Module**: Generates optimized waypoint grids for drone missions based on user-defined field dimensions and drone/camera configurations.  
- **Transfer Module**: Monitors the mission image folder, batches and uploads images asynchronously to an HPC system (e.g., OSC via Tapis), and initiates training or inference jobs.

The solution is intended for use in edge environments (e.g., agricultural fields) with limited computing resources and unreliable network connectivity.

### 2.3 Definitions, Acronyms, and Abbreviations

| Term        | Description                                                      |
|------------|------------------------------------------------------------------|
| HPC        | High Performance Computing                                       |
| Tapis      | API platform for remote job execution and data movement          |
| OSC        | Ohio Supercomputer Center                                       |
| Edge Device| Lightweight compute node deployed in the field (e.g., laptop or Intel NUC) |
| Waypoint   | GPS coordinate that a drone follows during a flight mission      |
| OpenPass   | Open-source drone mission controller used with Parrot Anafi      |
| Anafi      | A lightweight quadcopter drone by Parrot, used for aerial image capture |

---

## 3. Overall Description

### 3.1 Product Perspective

The system is part of a larger field sensing and cloud pipeline architecture, facilitating:

- Efficient **pre-flight mission planning**  
- **Real-time monitoring** of image generation  
- **Reliable image transfer** to remote servers (e.g., OSC)  
- **Triggering of downstream AI jobs** (e.g., segmentation or classification)

The architecture assumes no AI processing is performed on the drone; all inference/training occurs on the HPC backend.

### 3.2 User Classes and Characteristics

| User Class      | Description                                           | Technical Proficiency                 |
|-----------------|-------------------------------------------------------|---------------------------------------|
| Field Operator  | Defines field bounds and launches missions            | Basic computing and drone operation   |
| Edge Technician | Oversees edge device setup, network status            | Intermediate Linux/Python knowledge   |
| Researcher      | Uses the images for ML training or analysis           | Advanced HPC and ML experience        |
| System Admin    | Maintains Tapis jobs, credentials, logs, etc.         | Advanced (HPC & Networking)           |

### 3.3 Assumptions and Dependencies

- Edge devices run a Linux-based OS with Python 3.8+.  
- Parrot Anafi drone supports waypoint-based missions via OpenPass.  
- Tapis is used as the transfer and job orchestration backend.  
- Fields are rectangular, defined by four GPS points or area bounds.  
- Network connectivity is intermittent; uploads must be retry-safe.  
- Image duplication is possible; deduplication is enforced.

---

## 4. Functional Requirements

| ID    | Requirement                                                                                         |
|-------|-----------------------------------------------------------------------------------------------------|
| FR-1  | The system shall allow the user to input field dimensions or a set of GPS coordinates.             |
| FR-2  | The system shall compute a rectangular waypoint grid based on input parameters (altitude, FOV, sidelap, frontlap). |
| FR-3  | The system shall export a mission manifest compatible with OpenPass (e.g., CSV or JSON).           |
| FR-4  | The Transfer Module shall continuously monitor a configured mission output folder.                  |
| FR-5  | The system shall detect and batch new image files using configurable batch size and timeout.        |
| FR-6  | The Transfer Module shall support resumable and retry-safe uploads to the configured HPC destination using Tapis APIs. |
| FR-7  | The system shall trigger a predefined ML training/inference job after a successful image upload.    |
| FR-8  | The system shall perform deduplication to avoid retriggering jobs for already-processed data.       |
| FR-9  | The system shall log events, errors, and retries in structured logs for auditing and debugging.     |
| FR-10 | The system shall validate file integrity and completeness before triggering HPC jobs.               |
| FR-11 | The user shall be able to manually trigger retries for failed transfers.                            |
| FR-12 | The system shall store mission metadata (flight start time, image count, area coverage) per upload session. |

---

## 5. Non-Functional Requirements

| Category        | Requirement                                                                                                  |
|-----------------|--------------------------------------------------------------------------------------------------------------|
| Performance     | Upload throughput must tolerate at least 50% packet loss and still complete transfer within 2× real-time capture speed. |
| Reliability     | The system must retry failed uploads with exponential backoff and local checkpointing.                       |
| Scalability     | Should support at least 5 parallel missions running per day without system degradation.                      |
| Security        | All transfers must use encrypted channels (HTTPS, SFTP, or Tapis tokens); no credentials stored in plaintext.|
| Portability     | Should run on both lightweight laptops and Intel NUCs with 8GB RAM and limited storage.                      |
| Maintainability | Python code should follow PEP8 standards and be modular for reuse in other edge scenarios.                   |
| Usability       | Command-line interfaces must provide clear prompts and help options; errors must be human-readable.          |
| Fault Tolerance | Must recover from unexpected shutdowns by replaying or resuming partial transfers.                           |
| Storage Efficiency | Local storage used for batching should not exceed 80% of disk quota; older data is purged post-successful upload. |

---

## 6. Validation Criteria

| Requirement ID | Validation Strategy                                                                                     |
|----------------|--------------------------------------------------------------------------------------------------------|
| FR-1 to FR-3   | Provide test field boundaries and verify generated mission manifests via unit tests and manual map overlay. |
| FR-4 to FR-5   | Simulate file creation in mission folder and validate detection and batching logic.                     |
| FR-6           | Simulate upload with connection dropouts and ensure retry/recovery behavior functions as expected.      |
| FR-7           | Log job submission and match against uploaded files for consistency.                                    |
| FR-8           | Attempt duplicate uploads and validate job is not triggered twice.                                      |
| FR-10          | Use corrupted or incomplete files to verify integrity checks prevent job initiation.                    |
| FR-12          | Check metadata logs per upload session for completeness and accuracy.                                   |

---

## 7. Appendix

### 7.1 Glossary

| Term           | Meaning                                                          |
|----------------|------------------------------------------------------------------|
| Waypoint Plan  | A set of GPS points for drones to follow                        |
| Mission Manifest | Metadata file defining drone flight instructions              |
| Batch Upload   | Uploading multiple files together for efficiency                |
| Deduplication  | Avoiding repeated uploads or job submissions for the same data  |
