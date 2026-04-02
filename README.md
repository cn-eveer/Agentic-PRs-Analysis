# Agentic-PRs-Analysis

**Replication repository for the study
*“Why Are Agentic Pull Requests Accepted or Rejected? An Empirical Study”*.**

This repository contains datasets, annotation artifacts, and analysis scripts used to study agentic pull requests (PRs) on GitHub. It supports replication of empirical findings reported in the paper and the MSR Mining Challenge 2026.

Agentic PRs refer to pull requests created or modified by autonomous coding agents such as Copilot, Devin, Cursor, Claude Code, and OpenAI Codex.

---

## 1. Overview

Autonomous coding agents increasingly participate in collaborative software development by generating and submitting pull requests. This project investigates:

* how agentic PRs are accepted or rejected,
* the role of technical and workflow factors,
* human involvement in agent-generated contributions,
* empirical patterns across different agents.

The repository provides:

* manually annotated datasets,
* inter-rater agreement artifacts,
* reproducible analysis scripts,
* figures and tables reported in the paper.

---

## 2. Repository Structure

```
Agentic-PRs-Analysis/
│
├── README.md                  # Project documentation
├── LICENSE                    # Apache-2.0 license
├── requirements.txt           # Python dependencies
├── code_book_updated.md       # Annotation codebook
│
├── data/
│   ├── csv/                   # Annotated datasets and summary tables
│   ├── xlsx/                  # Master annotation workbooks
│   └── sample/                # Stratified samples for manual coding
│
├── script/
│   ├── samples.py             # Stratified sampling logic
│   ├── table1.py              # Table 1 reproduction script
│   ├── table2_table3.py       # Table 2 and Table 3 analysis
│   └── table1.ipynb           # Jupyter notebook for Table 1
│
├── paper/                     # Paper-related materials
│
├── replicationPackage/
│   └── outputs/               # Generated outputs and intermediate results
│
├── figure.png                 # Figures used in the paper
├── figure.svg
├── figure.drawio.png
```

---

## 3. Data Description

### 3.1 Manually Annotated Datasets (`data/csv/`)

The `csv` folder contains manually labeled PRs used in the MSR Mining Challenge 2026 and the main study, including:

* rejected agentic PR annotations,
* accepted agentic PR annotations,
* inter-rater agreement datasets,
* aggregated summary tables.

Annotations capture:

* agentic failure vs. non-agentic outcomes,
* feedback-loop patterns,
* human intervention signals,
* decision rationale categories.

### 3.2 Annotation Codebook

The file `code_book_updated.md` defines:

* labeling categories,
* decision criteria,
* representative examples,
* edge-case handling rules.

This ensures reproducibility of qualitative coding.

---

## 4. Analysis Scripts (`script/`)

### 4.1 Sampling Pipeline

`samples.py` reproduces the sampling logic aligned with Table 1 of the paper.

Steps:

1. Load large-scale GitHub PR data.
2. Apply filtering rules:

   * repositories with ≥ 500 stars,
   * closed pull requests only,
   * exclusion of bot-only PRs without human interaction.
3. Label PRs as accepted or rejected.
4. Recompute merged vs. rejected distributions per agent.
5. Generate stratified samples for:

   * inter-rater agreement,
   * manual qualitative analysis.

Outputs:

* `sample_check_rejected.csv`
* `sample_check_accepts.csv`
* `manual_check_rejected.csv`
* `manual_check_accepted.csv`

---

### 4.2 Table Reproduction

* `table1.py` / `table1.ipynb`: reproduces Table 1 (distribution of agentic PRs).
* `table2_table3.py`: reproduces Tables 2 and 3 (rejection reasons and feedback-loop analysis).

---

## 5. Replication Instructions

### 5.1 Environment Setup

```bash
pip install -r requirements.txt
```

(Recommended: use Python 3.10–3.11 and NumPy < 2 for compatibility.)

### 5.2 Run Analysis

```bash
python script/table1.py
python script/table2_table3.py
```

Or open the Jupyter notebook:

```bash
jupyter notebook script/table1.ipynb
```

---

## 6. Reproducibility Notes

* All sampling is stratified by agent to match the paper’s reported distributions.
* Manual annotations follow the published codebook.
* Unknown cases are treated as a separate category to avoid conflating missing evidence with confirmed failure.
* Outputs in `replicationPackage/outputs/` correspond to reported statistics and figures.

---

## 7. License

This project is licensed under the Apache-2.0 License. See the `LICENSE` file for details.

