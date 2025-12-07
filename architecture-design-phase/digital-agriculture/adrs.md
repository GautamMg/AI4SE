ADR-001 – Use Tapis API for Transfers and HPC Job Submission

Problem / Context

Need resumable, authenticated uploads and job submission to OSC under unreliable networks.

SRS: FR-6 (resumable Tapis uploads), FR-7 (trigger ML jobs), FR-9 (structured logs), FR-10 (integrity check); NFR-REL-001/002 (robust retry and partial recovery), NFR-SEC-001 (authenticated, encrypted access).

Stories: US-08 (View Transfer Progress), US-09 (Receive Job Completion Updates), US-10..US-13 (Auto-Detect, Batch, Retry, Resume).

Options

Use Tapis APIs for all uploads and job submission (tokens + HTTPS).

Custom SFTP/rsync over SSH, plus ad-hoc scripts for job submission.

Push to cloud object storage (e.g., S3) and run a watcher service on HPC.

Trade-offs

Option 1

Pros: Built-in auth, tokens, HTTPS (NFR-SEC-001); integrates directly with OSC; supports job status polling; good fit for FR-6/FR-7.

Cons: Adds dependency on Tapis availability and configuration; steeper learning curve.

Option 2

Pros: Simpler to prototype; fewer external dependencies.

Cons: Harder to make uploads idempotent and resumable (FR-6, FR-8); security and auditing become custom work; weaker alignment with NFR-REL-001/002.

Option 3

Pros: Very scalable; separates storage from compute.

Cons: Adds another moving part (object store); requires custom watcher on HPC; increases operational complexity and costs.

Decision

Adopt Option 1 (Tapis) as primary integration path for all uploads and job submission.

C4 links: TransferModule–TapisAPI–HPCCluster edges.

Revisit Criteria

OSC deprecates Tapis or mandates a different API.

Multi-cloud or multi-HPC support becomes a requirement beyond a single Tapis deployment.

Latency or throughput of Tapis cannot meet NFR-PER-002 for real missions.

ADR-002 – Separate Path Planner and Transfer Modules

Problem / Context

Mission planning is an interactive, sometimes offline task; transfer is a long-running, network-sensitive daemon.

SRS: FR-1..FR-3 (planning), FR-4..FR-8 (transfer), FR-12 (mission metadata); NFR-USA-001 (clear feedback on flight path), NFR-PORT-001 (edge device support).

Stories: US-01..US-07 (planning and offline support) vs US-10..US-16 (automation, dedup, storage management).

Options

Single monolithic CLI combining planning and transfer.

Two modules: PathPlannerModule and TransferModule as separate processes on same edge device.

Multiple microservices with network APIs between them.

Trade-offs

Option 1

Pros: Simple packaging and deployment.

Cons: Hard to keep transfer logic running continuously; mixes concerns; more fragile under crashes.

Option 2

Pros: Clear separation of responsibilities; transfer can run headless as a daemon; planning can be used offline; simpler than microservices.

Cons: Requires coordination via EdgeDatabase and EdgeFileStore.

Option 3

Pros: Maximum flexibility and scaling.

Cons: Overkill for a single edge device; adds network, discovery, and security overhead.

Decision

Choose Option 2. Implement PathPlannerModule and TransferModule as separate processes communicating only via EdgeDatabase and EdgeFileStore.

C4 links: separate containers PathPlannerModule, TransferModule.

Revisit Criteria

Requirement to deploy planner and transfer components on different hardware.

Requirement to offer planning as a remote service to multiple field devices.

ADR-003 – Use SQLite Edge Database for Metadata, Dedup, and Recovery

Problem / Context

System must avoid recomputation (FR-8), support retries and resume (FR-6, FR-11), and store mission metadata (FR-12) on a constrained edge device.

NFR-REL-001/002 (robust retry and partial recovery), NFR-PER-002 (continuous monitoring latency), NFR-PORT-001 (NUC/laptop).

Stories: US-11 (Batch Uploads), US-12 (Retry Failed Transfers), US-13 (Resume Interrupted Transfers), US-14 (Deduplicate Data).

Options

SQLite database (EdgeDatabase) with explicit schemas for missions, batches, hashes, and jobs.

Plain text/JSON log files and in-memory structures.

Remote database on HPC or cloud.

Trade-offs

Option 1

Pros: ACID semantics, transactional updates; simple to query; well-suited for single-node edge; supports strong recovery semantics.

Cons: Slight complexity overhead vs raw files; requires schema management.

Option 2

Pros: Very simple, no DB engine.

Cons: Harder to query; brittle dedup and recovery; increased risk of inconsistency after crashes.

Option 3

Pros: Centralized visibility.

Cons: Depends on network; violates offline/low-connectivity constraint; conflicts with NFR-REL-001.

Decision

Use SQLite as EdgeDatabase for mission metadata, dedup hashes, transfer sessions, and job status.

C4 links: PathPlannerModule–EdgeDatabase, TransferModule–EdgeDatabase.

Revisit Criteria

Edge devices become extremely resource constrained (e.g., limited write cycles or storage).

Scale requirement grows to many concurrent missions per device that stress SQLite.

ADR-004 – Batch-Based Transfer Using Size and Time Thresholds

Problem / Context

Need to detect and batch new images (FR-5), support resumable uploads (FR-6, FR-11, FR-12), and avoid recomputation (FR-8) while respecting limited storage.

NFR-PER-002 (monitoring latency), NFR-REL-001/002 (retry and recovery), NFR-SCA-001 (support multiple missions), NFR-USE-003 (clear CLI feedback).

Stories: US-10 (Auto-Detect New Images), US-11 (Batch Uploads), US-16 (Manage Local Storage).

Options

Upload every file immediately as it appears (no batching).

Pure time-based batching (e.g., every N seconds).

Pure size/count-based batching (e.g., every M images).

Hybrid: whichever comes first (time or size threshold) triggers a batch.

Trade-offs

Option 1

Pros: Lowest latency per file.

Cons: Very chatty to Tapis; poor efficiency; harder to resume; may overload HPC jobs with tiny sessions.

Options 2 & 3

Pros: Predictable behavior in one dimension.

Cons: Time-only may lead to small batches in sparse missions; size-only may delay uploads too long.

Option 4

Pros: Bounded latency and bounded batch size; good fit for intermittent connectivity.

Cons: Configuration complexity (two thresholds) and test matrix grows.

Decision

Adopt hybrid batch policy (time and count thresholds) in TransferModule. Batch IDs and session IDs are persisted in EdgeDatabase and reused for idempotent retries.

C4 links: TransferModule–EdgeFileStore, TransferModule–EdgeDatabase, TransferModule–TapisAPI.

Revisit Criteria

New NFRs demand strict latency bounds tighter than current thresholds.

HPC or Tapis impose strict limits on batch size or request frequency that require retuning.