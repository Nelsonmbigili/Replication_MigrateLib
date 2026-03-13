
## 1. Project Title and Overview

**Namu Go**  (New York University Abu Dhabi) and **Nelson Mbigili**  (New York University Abu Dhabi) 



- **Paper Title**: Replication of *MigrateLib*: A Tool for End-to-End Python Library Migration
- **Authors**: Mohayeminul Islam, Ajay Kumar Jha, May Mahmoud, and Sarah Nadi
- **Replication Team**: Namu Go and Nelson Mbigili
- **Course**: CS-UH 3260 Software Analytics, NYUAD
- **Brief Description**: 
    - **Original Paper Summary**:

   The original paper introduces **MigrateLib**, an end-to-end tool for automating Python library migration by combining **Large Language Models (LLMs)** with **static and dynamic program analysis**. The authors show that while LLM-only migration achieves moderate correctness, integrating analysis-driven post-processing substantially improves migration success across real-world codebases.

  - **Replication Scope Summary**:

   This repository replicates and evaluates key claims from the original paper. In particular, this replication:
    1. Evaluates **RQ1.1 outcomes** by randomly selecting 10 migrations and manually checking the LLM migration vs. the labeled code changes in [PyMigBench](https://github.com/ualberta-smr/PyMigBench) to access validity

    2. Reproduces the **RQ2-1 experiment**, evaluating migration correctness across **717** real-world Python library migration scenarios.
    3. Assesses whether the effectiveness improvements reported for the full MigrateLib pipeline can be independently reproduced.
  
  All scripts, datasets, and evaluation artifacts needed to reproduce the replication results are provided in this repository.
---

##  2. Repository Structure 


###

This repository has the following structure

```
## Repository Structure

README.md              # Main documentation for the replication study
Instructs.md           # Step-by-step instructions for running the replication
datasets/              # Datasets and benchmarks used in the replication study
scripts/               # Scripts used for running experiments and analysis
                           - Includes original, modified, and newly created scripts
LibMig/                # Symbolic link to the original MigrateLib tool source code
migratelib/            # Original MigrateLib tool source code (as provided by authors)
LibMig-paper/          # Replication paper source with replication datasets 
LibMig-paper-org/      # Original paper source files produced with original dataset
results/               # Original paper results of migrations
replicationResults/    # Our replication results used in analysis and reporting
```


### 3. Setup Instructions
#### Prerequisites

- **Operating System:** Linux or macOS  
- **Tools:** `git`, `pip`, `virtualenv` or `venv`
- **LLM Access:** API access to an OpenAI-compatible LLM service  
 

> All required Python packages and exact versions are specified in `requirements.txt`.

---

#### Installation

1. **Clone the repository**
   ```bash
   git clone <url>
   ```

### 4. GenAI Usage

- **Tool Used:** [Google Gemini](https://gemini.google.com/)

- **How It Was Used:**
  - To understand the overall **codebase structure and execution flow** in early stages
  - To quickly identify and understand the **purpose and usage of various Python libraries** involved in the migration pipeline, supporting evaluation and analysis.
  - To assist with **debugging errors**, particularly those related to **package version mismatches** and **virtual environment setup** issues.

