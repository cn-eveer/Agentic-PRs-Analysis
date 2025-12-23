#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import pandas as pd

# ========== CONFIGURATION (EDIT ONLY THIS SECTION) ==========
# DATA_SOURCE options: 'local' (read local parquet under DATA_DIR) or 'hf' (read via HuggingFace URI)
DATA_SOURCE: str = "hf"

# For local mode: set DATA_DIR to a path containing parquet files or leave None to auto-detect
DATA_DIR: Optional[Path] = None

# For HF mode: base URI prefix for huggingface dataset parquet files
HF_BASE: str = "hf://datasets/hao-li/AIDev"

# Hard-coded filter per request: do not change
MIN_STARS: int = 500  # filter: repos with stars >= 500 (hard-coded)

AGENTS: Sequence[str] = ["Claude_Code", "Copilot", "Cursor", "Devin", "OpenAI_Codex"]

# Bot list (taken from Untitled1.ipynb)
BOT_LIST: Sequence[str] = [
    "copilot-swe-agent[bot]",
    "cursor[bot]",
    "gemini-code-assist[bot]",
    "copilot-pull-request-reviewer[bot]",
    "coderabbitai[bot]",
    "ellipsis-dev[bot]",
    "greptile-apps[bot]",
    "entelligence-ai-pr-reviews[bot]",
    "Copilot",
    "github-advanced-security[bot]",
]

REQUIRED_FILES = ["pull_request.parquet", "repository.parquet"]


def relpath_to_repo(p: Path, repo_root: Optional[Path] = None) -> str:
    """Friendly relative-path printer (avoid showing absolute paths)."""
    try:
        if repo_root is None:
            repo_root = Path(".").resolve()
        return p.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return p.as_posix()


def is_dataset_dir(p: Path) -> bool:
    return all((p / f).is_file() for f in REQUIRED_FILES)


def find_dataset_dir(data_dir_hint: Optional[Path] = None) -> Optional[Path]:
    candidates = []
    if data_dir_hint:
        candidates.append(Path(data_dir_hint))
    candidates.extend([Path("."), Path(".."), Path("../..")])

    for cand in candidates:
        cand = Path(cand)
        # 1) exact match
        if is_dataset_dir(cand):
            return cand.resolve()
        # 2) immediate subdirectories
        if cand.is_dir():
            for sub in cand.iterdir():
                if sub.is_dir() and is_dataset_dir(sub):
                    return sub.resolve()
    return None


def read_parquet_file(
    name: str,
    *,
    columns: Optional[Sequence[str]] = None,
    base_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """Unified reader: local path or HF URI depending on DATA_SOURCE."""
    if DATA_SOURCE == "hf":
        uri = f"{HF_BASE}/{name}"
        return pd.read_parquet(uri, columns=list(columns) if columns else None)
    if base_dir is None:
        raise ValueError("base_dir is required when DATA_SOURCE='local'")
    return pd.read_parquet(base_dir / name, columns=list(columns) if columns else None)


def main() -> None:
    # Setup depending on DATA_SOURCE
    if DATA_SOURCE == "local":
        base = find_dataset_dir(DATA_DIR)
        if base is None:
            raise FileNotFoundError(
                "Dataset directory could not be automatically detected.\n"
                "Set DATA_DIR to the folder containing the parquet files.\n"
                "Example: DATA_DIR = Path('/path/to/dataset_dir')"
            )
        repo_root = base.parent.resolve()
        out_dir = repo_root / "replicationPackage" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        print("Dataset dir detected:", relpath_to_repo(base, repo_root))
    else:
        base = None
        repo_root = Path(".").resolve()
        out_dir = repo_root / "replicationPackage" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        print("Using HF dataset base:", HF_BASE)

    # Load minimal columns only (fast + reproducible)
    repos = read_parquet_file(
        "repository.parquet", columns=["id", "stars"], base_dir=base
    )
    prs = read_parquet_file(
        "pull_request.parquet",
        columns=["id", "repo_id", "agent", "user", "state", "merged_at", "html_url"],
        base_dir=base,
    )
    comments = read_parquet_file(
        "pr_comments.parquet", columns=["pr_id", "user_type"], base_dir=base
    )

    print("repos:", repos.shape)
    print("prs:", prs.shape)
    print("comments:", comments.shape)

    # Step 1: Universe selection (paper-aligned): repos with stars>=500, and closed PRs
    repo_ids = set(repos.loc[repos["stars"] >= MIN_STARS, "id"].astype(int).tolist())
    print("repos with stars>=500:", len(repo_ids))

    selected = prs[
        (prs["repo_id"].astype(int).isin(repo_ids)) & (prs["state"] == "closed")
    ].copy()
    selected_ids = set(selected["id"].astype(int).tolist())
    print("selected closed agentic PRs:", len(selected_ids))

    # Exclude bot-authored PRs with no human (User) comments
    bot_assigned = selected[selected["user"].isin(BOT_LIST)].copy()
    print("bot_assigned (author in BOT_LIST):", len(bot_assigned))

    user_commented_pr_ids = set(
        comments.loc[comments["user_type"] == "User", "pr_id"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    excluded = bot_assigned[
        ~bot_assigned["id"].astype(int).isin(user_commented_pr_ids)
    ].copy()
    excluded_ids = set(excluded["id"].astype(int).tolist())

    kept_ids = selected_ids - excluded_ids
    print("excluded (bot_assigned & no User comments):", len(excluded_ids))
    print("kept:", len(kept_ids))

    kept = selected[~selected["id"].astype(int).isin(excluded_ids)].copy()
    kept["is_merged"] = kept["merged_at"].notna()

    # Aggregate by agent
    table = (
        kept.groupby("agent")
        .agg(total=("id", "count"), merged=("is_merged", "sum"))
        .reset_index()
    )
    table["rejected"] = table["total"] - table["merged"]

    # Keep only known agents in a fixed order
    order = {a: i for i, a in enumerate(AGENTS)}
    table1 = table[table["agent"].isin(AGENTS)].copy()
    table1["__order"] = table1["agent"].map(order)
    table1 = (
        table1.sort_values("__order").drop(columns=["__order"]).reset_index(drop=True)
    )

    # Print results
    print("\n=== Table 1 (by agent) ===")
    print(table1.to_string(index=False))

    total_total = int(table1["total"].sum())
    total_merged = int(table1["merged"].sum())
    total_rejected = int(table1["rejected"].sum())
    print("\nTOTAL", total_total, total_merged, total_rejected)

    print("\nExcluded count:", len(excluded_ids))
    print("Kept count:", len(kept_ids))
    print("Sample excluded ids (first 10):", sorted(excluded_ids)[:10])
    print("Sample kept ids (first 10):", sorted(kept_ids)[:10])


if __name__ == "__main__":
    main()
