# AI-Assisted SDLC for Research — Overview & Repo Guide

## What we’re doing

We’re building AI-assisted tooling that helps researchers turn early ideas into working products with minimal friction. The workflow is simple and repeatable: start from approved requirements, generate clear architecture and design, then produce a small, runnable implementation slice—measurable, traceable, and easy to extend.

## Why this matters

* Faster path from concept → blueprint → running code
* Decisions, boundaries, and security are explicit and testable
* Same process runs across our three research products for easy comparison

---

## Phases at a glance

**Requirements (inputs)**
AI-generated, IEEE-aligned SRS and INVEST-checked user stories provide the authoritative “what” and “why”.

**Architecture & Design (blueprint)**
C4 Context/Container diagrams, ADRs, Use Case diagram, STRIDE summary, and sequence diagrams translate requirements into a clear, testable plan.

**Implementation (starter code)**
A small, end-to-end slice (request → validation → processing → persistence → response) with contracts, tests, Docker, and a Quickstart. Focused, not overbuilt.

---

## Repository structure

```
/requirement-phase/               # SRS and User Stories (inputs)
/architecture-design-phase/      # C4, ADRs, Use Cases, STRIDE, Sequences (by project and AI tool)
/implementation-phase/             # Runnable slices (service, tests, API spec, ops, README)
/elaboration-phase/               # Elaboration of problem statement .
/inception-phase/                    # Incepting the research objectives .
```

Each **phase** (e.g., `requirement-phase`, `architecture-design-phase`) has its own subfolders for all the three test subjects (e.g., `animal-ecology`, `digital-agriclture`, `ao-oct`) containing individual artifacts.
---

## How to read this repo (quick path)

1. **Start with inputs** → open `/requirement-phase/` to see what the system must do.
2. **Understand the blueprint** → in `/architecture-design-phase/<project>/`, read in order:
   `01 Context` → `02 Container` → `03 ADRs` → `04 Use Cases` → `05 STRIDE` → `06 Sequences`.
3. **Implementation code base** → Check `/implementation-phase/<project>`
4. **Verify links** → use `/architecture-design-phase/<>project/rtm.csv` to jump from a requirement ID to the related ADRs, diagrams, endpoints, and tests.
5. **Compare AI tools** → open the same numbered file (e.g., `03-adrs.md`) across tool folders.

---

## Artifact guide (what and why)

* **C4 — System Context**: shows the system in its environment (actors, externals, relationships).
* **C4 — Container**: shows deployable parts and data stores with responsibilities and key interfaces.
* **ADRs**: record important choices, alternatives, trade-offs, and revisit criteria.
* **Use Case diagram**: keeps functional intent visible and tied to stories.
* **STRIDE summary**: lists threats at each boundary with planned mitigations.
* **Sequence diagrams**: make key flows concrete (success, retries, errors).
* **Implementation slice**: minimal service + OpenAPI slice + tests + Dockerfile + Quickstart.

---

## How we build each implementation slice (high level)

* **Inputs**: Project Context, SRS, User Stories, and the Architecture & Design workproducts
* **Select a few stories**: highest value or risk
* **Keep names consistent**: exactly match C4/ADRs across code and tests
* **Ship a complete starter**: contracts, code, tests, Docker, README—runnable as-is

---

## How we measured quality

[We shd refer to IBM report and write a comprehensive content here]

---

## References (slide PDFs)

* **Inception Phase PDF:** [Need to add link](sandbox:/mnt/data/Architecture%20Phase.pdf)
* **Requirement analysis Phase PDF:** [Need to add link](sandbox:/mnt/data/Architecture%20Phase.pdf)
* **Architecture Phase PDF:** [Need to add link](sandbox:/mnt/data/Architecture%20Phase.pdf)
* **Implementation Phase PDF:** [Need to add link](sandbox:/mnt/data/Implementation_phase%20%281%29.pdf)

---

## Where to start

* Repo home: [https://github.com/GautamMg/AI4SE](https://github.com/GautamMg/AI4SE)
* Quick tour: read `/requirement-phase/`, then one project under `/architecture-design-phase/`, then run its slice in `/Implementation/`

That’s the whole story: requirements in, architecture & design to clarify, a small runnable slice to prove the path, and simple metrics so we know it’s working.
