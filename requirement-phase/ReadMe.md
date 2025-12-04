# Requirements Analysis Phase – Summary

This folder contains the **Requirements Analysis Report** for our AI4SE study.  
In this phase, we systematically explored how different AI tools can assist with core requirements artifacts—primarily **Software Requirements Specifications (SRS)** and **user stories**—across three domains: **Animal Ecology**, **AO-OCT**, and **Digital Agriculture**. :contentReference[oaicite:0]{index=0}  

The report describes how a common project context and carefully structured prompts were used across tools (ChatGPT 4o, Gemini 2.5 Flash, Perplexity Comet, Claude Sonnet 4.5) to generate these artifacts, and how the results were evaluated against industry-aligned frameworks:

- **SRS**: assessed on completeness, correctness, unambiguity, consistency, verifiability, and understandability, with structure aligned to IEEE-style SRS. :contentReference[oaicite:1]{index=1}  
- **User stories**: assessed against the **INVEST** criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable). :contentReference[oaicite:2]{index=2}  

Overall, the report finds that all tools can produce structured, usable first drafts, but differ in depth, clarity, and testability. Claude tends to be the most comprehensive (especially on assumptions and validation), Gemini is concise but lighter on non-functional and security details, while ChatGPT and Perplexity often produce similar, developer-friendly layouts that still need sharpening around metrics and edge cases. :contentReference[oaicite:3]{index=3}  

For user stories, ChatGPT and Claude usually produce clearer, outcome-focused stories; Gemini and Perplexity sometimes combine multiple goals or add fixed details that reduce negotiability. Across tools, stories are generally estimable and small, but many would benefit from more explicit user value statements and crisper acceptance criteria. :contentReference[oaicite:4]{index=4}  

---

## Overview Diagram (Artifacts, Domains, Evaluation)

```mermaid
flowchart TD

%% MAIN NODE
A([**📄 Requirements Analysis Report**])

%% HIGH-LEVEL BRANCHES
A --> B{**Artifacts**}
A --> E{**Evaluation Frameworks**}
A --> H{**AI Tools Used**}

%% ARTIFACT TYPES
B --> C([**SRS Documents**])
B --> D([**User Stories**])

%% SRS PER PROJECT
C --> C1([**🐾 AE – SRS**<br/>AE_SRS.ipynb])
C --> C2([**👁️ AO-OCT – SRS**<br/>AOOCT_SRS.ipynb])
C --> C3([**🌱 DigAg – SRS**<br/>DigAg_SRS.ipynb])

%% USER STORIES PER PROJECT
D --> D1([**🐾 AE – User Stories**<br/>AE_user_stories.ipynb])
D --> D2([**👁️ AO-OCT – User Stories**<br/>AOOCT_user_stories.ipynb])
D --> D3([**🌱 DigAg – User Stories**<br/>DigAg_User_Stories.ipynb])

%% EVALUATION BRANCH
E --> F([**SRS Metrics**<br/>Completeness, Correctness,<br/>Unambiguity, Consistency,<br/>Verifiability, Understandability])
E --> G([**INVEST for User Stories**<br/>Independent, Negotiable,<br/>Valuable, Estimable,<br/>Small, Testable])

%% TOOLS
H --> H1([ChatGPT 4o])
H --> H2([Gemini 2.5 Flash])
H --> H3([Perplexity – Comet])
H --> H4([Claude 4.5 Sonnet])

%% COLORS / STYLING
style A fill:#fff2cc,stroke:#cc9900,stroke-width:2px,rx:12,ry:12
style B fill:#f0f0f0,stroke:#666,stroke-width:1.5px,rx:10,ry:10
style E fill:#f0f0f0,stroke:#666,stroke-width:1.5px,rx:10,ry:10
style H fill:#f0f0f0,stroke:#666,stroke-width:1.5px,rx:10,ry:10

style C1 fill:#ffe6e6,stroke:#cc0000,stroke-width:2px,rx:12,ry:12
style C2 fill:#e6ffe6,stroke:#009900,stroke-width:2px,rx:12,ry:12
style C3 fill:#e6ecff,stroke:#0033cc,stroke-width:2px,rx:12,ry:12

style D1 fill:#ffe6e6,stroke:#cc0000,stroke-width:1.5px,rx:10,ry:10
style D2 fill:#e6ffe6,stroke:#009900,stroke-width:1.5px,rx:10,ry:10
style D3 fill:#e6ecff,stroke:#0033cc,stroke-width:1.5px,rx:10,ry:10
