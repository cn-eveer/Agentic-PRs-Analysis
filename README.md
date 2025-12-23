# Agentic-PRs-Analysis

**Repository for replication of our studies of _“Why Are Agentic Pull Requests Accepted or Rejected? An Empirical Study”_.** :contentReference[oaicite:0]{index=0}

This project contains the data and scripts used for analyzing agentic pull requests on GitHub — that is, pull requests created or assisted by autonomous coding agents.

## 📌 Overview

In the era of agentic software development, autonomous agents (LLM-based systems that can read and modify code) are increasingly creating and submitting pull requests. This repository supports replication and exploration of a study into:

- **Agentic pull requests (PRs)** — PRs authored or assisted by automated coding agents.
- **Acceptance and rejection patterns** — Analysis of what influences the likelihood of a PR being merged or rejected.
- **Empirical data and scripts** — Includes datasets and scripts used for statistical and exploratory analysis.

> This repository is meant to help researchers and practitioners understand how autonomous agents behave in real collaborative code settings.

## Repository Structure

### `data/`
Contains **manually annotated datasets** used for validation and qualitative analysis in the study and the MSR Mining Challenge 2026.

- `csv/`: Exported annotation results, including:
  - Interrater agreement files from multiple human coders
  - Manual annotations for accepted and rejected agentic pull requests
  - Summary tables aggregating annotation results
- `xlsx/`: Master Excel workbooks used for annotation and agreement analysis ()

These files capture human judgments on why agentic pull requests were accepted or rejected.

### `script/`
Contains **analysis scripts and Jupyter notebooks** used to reproduce the empirical results in the paper.

Scripts load large-scale pull request data (locally or via Hugging Face), apply paper-aligned filtering rules (e.g., star threshold, closed PRs, bot filtering), and compute statistics such as merged vs. rejected PRs by agent.

#### Sampling Script (Table-1–Aligned)

This script reproduces the **Table 1 filtering logic** from the paper and generates datasets for **manual review** and **inter-rater agreement**.

**What the script does:**
1. Loads large-scale GitHub PR data (locally or via Hugging Face).
2. Applies paper-aligned filters:
   - repositories with ≥ 500 stars,
   - closed pull requests only,
   - excludes bot-authored PRs with no human comments.
3. Labels remaining PRs as:
   - **accepted** (merged),
   - **rejected** (not merged).
4. Recomputes **Table 1** (merged vs. rejected counts per agent).
5. Uses the Table 1 totals to create **stratified samples by agent** for:
   - inter-rater agreement checks, and
   - manual inspection.

**Outputs (CSV files):**
- `sample_check_rejected.csv` – rejected PRs for agreement validation
- `sample_check_accepts.csv` – accepted PRs for agreement validation
- `manual_check_rejected.csv` – rejected PRs for manual analysis
- `manual_check_accepted.csv` – accepted PRs for manual analysis

All sampling is reproducible and stratified by agent, ensuring consistency with the paper’s reported statistics.

---

This project is licensed under the **Apache-2.0 License** — see the [LICENSE](LICENSE) file for details.

