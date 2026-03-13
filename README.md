
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
- **Programming Labguage:** Python 
- **Tools:** `git`, `pip`, `virtualenv` or `venv`
- **LLM Access:** API access to an OpenAI-compatible LLM service  
 

> All required Python packages and exact versions are specified in `requirements.txt`.

---

#### Installation

1. **Clone the repository**
   ```bash
   git clone <repository url>
   cd Replication_MigrateLib
   ```
2. The paths are already configured in the path.py in utils folder

3. For **RQ1.1** We selected 10 migrations from [PyMigBench](https://github.com/ualberta-smr/PyMigBench) and found their equivalent LLM migrations in [An Empirical Study of Python Library Migration Using Large Language Models - artifacts](https://figshare.com/articles/conference_contribution/An_Empirical_Study_of_Python_Library_Migration_Using_Large_Language_Models_-_artifacts/25459000) These are alredy provided with our analysis.
4. For **RQ1.2** Create a file **/scripts/secrets/secrets.yaml** where environment variables will live in the format below:
``` bash
LIBIO_API_KEY: "Your Key"
GITHUB_ACCESS_TOKENS: 
  - "Your Yoken"
OPENAI_API_KEY: "Your API Key"
VALIDATION_GSHEET:
  file: "Google Sheet API Key"
  lib_pairs_sheet: ""
REPO_ROOT: null
```


### 4. GenAI Usage

- **Tool Used:** [Google Gemini](https://gemini.google.com/)

- **How It Was Used:**
  - To understand the overall **codebase structure and execution flow** in early stages
  - To quickly identify and understand the **purpose and usage of various Python libraries** involved in the migration pipeline, supporting evaluation and analysis.
  - To assist with **debugging errors**, particularly those related to **package version mismatches** and **virtual environment setup** issues.

