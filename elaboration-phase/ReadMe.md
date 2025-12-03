# Research Elaboration Summary

This folder contains the **Elaboration / Risk-Removal / Background Research Report** for our AI4SE study.  
The document expands on the inception-phase work by surveying related literature, defining research questions, outlining methodology, and identifying the workproducts we will generate across the three projects—**Animal Ecology**, **AO-OCT**, and **Digital Agriculture**.

The report covers:
- Background scan of each project domain  
- Literature review strategy  
- Research questions (AI usefulness, tool comparison, automation balance)  
- Proposed workproducts in requirements analysis and design support  
- Links to prototypes and Colab notebooks  
- Observations on AI-generated PRDs and diagrams  

---

## Overview Diagram (with Colab Links)

```mermaid
flowchart TD

A[Research Elaboration Report] --> B{Sections}

B --> C[Background & Related Work]
B --> D[Research Questions]
B --> E[Methodology]
B --> F[Proposed Workproducts]

%% Project Branches
A --> G{Projects}

G --> H[Animal Ecology<br><a href='https://colab.research.google.com/github/...'>Colab: Requirement Analysis</a>]
G --> I[AO-OCT<br><a href='https://colab.research.google.com/github/...'>Colab: Diagrams / Flow</a>]
G --> J[Digital Agriculture<br><a href='https://colab.research.google.com/github/...'>Colab: System Details</a>]

%% Workproduct Branch
F --> K[Requirements & Analysis<br>Stories + Acceptance Criteria]
F --> L[Non-Functional Requirements<br>Measurable Metrics]
F --> M[Design Support<br>Architecture + Flow Diagrams]

%% Observations
A --> N[AI Tool Observations]
N --> O[PRD Quality<br>Successes + Gaps]
N --> P[Diagram Quality<br>(Often Needs Manual Fixes)]
