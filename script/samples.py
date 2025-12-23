from pathlib import Path
from typing import Optional, Sequence
import pandas as pd
from sklearn.model_selection import train_test_split

# ================= CONFIG =================
DATA_SOURCE = "hf"
HF_BASE = "hf://datasets/hao-li/AIDev"
MIN_STARS = 500
RANDOM_STATE = 72
VALIDATE_AGREEMENT_SAMPLE = 30

AGENTS = ["Claude_Code", "Copilot", "Cursor", "Devin", "OpenAI_Codex"]

BOT_LIST = [
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

OUT_DIR = Path("./data/sample")
OUT_DIR.mkdir(exist_ok=True)


# =============== HELPERS =================
def read_parquet(name: str, columns=None) -> pd.DataFrame:
    uri = f"{HF_BASE}/{name}"
    return pd.read_parquet(uri, columns=columns)


def stratified_n_sample(df, n, col):
    n = min(n, len(df))
    if n == 0:
        return df.iloc[0:0], df
    if n == len(df):
        return df, df.iloc[0:0]
    a, b = train_test_split(
        df,
        test_size=len(df) - n,
        stratify=df[col],
        random_state=RANDOM_STATE,
    )
    return a, b


# =============== LOAD DATA =================
repos = read_parquet("repository.parquet", ["id", "stars"])
prs = read_parquet(
    "pull_request.parquet",
    ["id", "repo_id", "agent", "user", "state", "merged_at", "html_url"],
)
comments = read_parquet("pr_comments.parquet", ["pr_id", "user_type"])

# =============== TABLE 1 LOGIC =================
repo_ids = set(repos.loc[repos["stars"] >= MIN_STARS, "id"].astype(int))

selected = prs[
    (prs["repo_id"].astype(int).isin(repo_ids)) & (prs["state"] == "closed")
].copy()

bot_assigned = selected[selected["user"].isin(BOT_LIST)]

human_commented_ids = set(
    comments.loc[comments["user_type"] == "User", "pr_id"].astype(int)
)

excluded_ids = set(
    bot_assigned.loc[
        ~bot_assigned["id"].astype(int).isin(human_commented_ids), "id"
    ].astype(int)
)

kept = selected[~selected["id"].astype(int).isin(excluded_ids)].copy()
kept["is_merged"] = kept["merged_at"].notna()

table1 = (
    kept.groupby("agent")
    .agg(total=("id", "count"), merged=("is_merged", "sum"))
    .reset_index()
)
table1["rejected"] = table1["total"] - table1["merged"]
table1 = table1[table1["agent"].isin(AGENTS)]

# =============== SPLIT ACCEPT / REJECT =================
combined_accepted = kept[kept["is_merged"]].copy()
combined_rejected = kept[~kept["is_merged"]].copy()

# Sample sizes derived from Table 1
ACCEPT_SAMPLE_SIZE = int(table1["merged"].sum())
REJECT_SAMPLE_SIZE = int(table1["rejected"].sum())

# =============== AGREEMENT SAMPLES =================
sample_check_rejected, reject_remaining = stratified_n_sample(
    combined_rejected, VALIDATE_AGREEMENT_SAMPLE, "agent"
)
sample_check_accepts, accept_remaining = stratified_n_sample(
    combined_accepted, VALIDATE_AGREEMENT_SAMPLE, "agent"
)

# =============== MANUAL CHECK SAMPLES =================
manual_check_rejected, _ = stratified_n_sample(
    reject_remaining, REJECT_SAMPLE_SIZE, "agent"
)
manual_check_accepted, _ = stratified_n_sample(
    accept_remaining, ACCEPT_SAMPLE_SIZE, "agent"
)

EXPORT_COLS = ["id", "html_url", "agent"]

# =============== WRITE OUTPUT =================
sample_check_rejected[EXPORT_COLS].to_csv(
    OUT_DIR / "sample_check_rejected.csv", index=False
)
sample_check_accepts[EXPORT_COLS].to_csv(
    OUT_DIR / "sample_check_accepts.csv", index=False
)
manual_check_rejected[EXPORT_COLS].to_csv(
    OUT_DIR / "manual_check_rejected.csv", index=False
)
manual_check_accepted[EXPORT_COLS].to_csv(
    OUT_DIR / "manual_check_accepted.csv", index=False
)

print("CSV files written successfully.")
