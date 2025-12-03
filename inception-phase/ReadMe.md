# Inception Phase Summary

This folder contains the inception-phase report for our AI4SE study.  
The document outlines how the team will evaluate AI tools across the software development lifecycle—requirements, architecture, implementation, testing, documentation, and project management—using a shared measurement framework applied to three domains: Animal Ecology, AO-OCT retinal imaging, and Digital Agriculture. :contentReference[oaicite:0]{index=0}

The report also defines success metrics, human-vs-automation guardrails, a 3-phase work plan, and key risks such as tool instability, privacy concerns, and over-dependence on AI.

---

## Overview Diagram

```mermaid
flowchart TD

A[Inception Phase Report] --> B{Evaluation Scope}

B --> C[Requirements Analysis]
B --> D[Architecture & Design]
B --> E[Implementation Support]
B --> F[Test Generation]
B --> G[Documentation & PM]

A --> H{Projects Studied}
H --> I[Animal Ecology]
H --> J[AO-OCT Imaging]
H --> K[Digital Agriculture]

A --> L{3-Phase Plan}
L --> M[Phase 1: Frame]
L --> N[Phase 2: Compare]
L --> O[Phase 3: Synthesize & Deliver]
