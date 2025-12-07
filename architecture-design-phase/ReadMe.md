# Architecture & Design Phase — Summary

This folder contains the Architecture & Design Phase report, which builds on the SRS and User Stories from the requirements phase.  
The goal of this phase is to turn project requirements into a testable, review-ready architecture with clear traceability across all artifacts. :contentReference[oaicite:0]{index=0}

The report explains how AI tools (ChatGPT, Claude, Gemini, Mistral) were used to generate architecture artifacts and how those artifacts were evaluated qualitatively and quantitatively.

---

## What This Phase Produces

Using the SRS and User Stories as inputs, this phase generates:

1. C4 System Context diagram  
2. C4 Container diagram  
3. Architecture Decision Records (ADRs)  
4. Use Case diagram  
5. STRIDE threat summary  
6. Sequence diagrams for key flows  
7. Traceability Matrix (RTM) linking requirements, ADRs, and diagrams :contentReference[oaicite:1]{index=1}  

These artifacts are produced for each project (Animal Ecology, AO-OCT, Digital Agriculture) and for each AI tool, using a consistent file structure.

---

## High-Level Workflow (Inputs → AI Tools → Artifacts → Evaluation)

```mermaid
flowchart LR

SRS[SRS]
Stories[User Stories]
Tools[AI Tools: ChatGPT, Claude, Gemini, Mistral]

SRS --> Tools
Stories --> Tools

Tools --> Ctx[C4 System Context]
Tools --> Cntr[C4 Container Diagram]
Tools --> ADRs[Architecture Decision Records]
Tools --> UC[Use Case Diagram]
Tools --> STR[STRIDE Threat Summary]
Tools --> Seq[Sequence Diagrams]
Tools --> RTM[Traceability Matrix]

Ctx --> Eval[Architecture Review]
Cntr --> Eval
ADRs --> Eval
UC --> Eval
STR --> Eval
Seq --> Eval
RTM --> Eval

Eval --> Metrics[Metrics: Coverage, STRIDE depth, ADR breadth, Document quality]
