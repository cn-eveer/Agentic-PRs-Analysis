import pandas as pd


def summarize_table(df):

    ## Create summary table
    summary = df.groupby(["agent", "Decision"]).size().unstack(fill_value=0)

    # Add Total column
    summary["Total"] = summary.sum(axis=1)

    # Add Grand Total row
    summary.loc["Grand Total"] = summary.sum(axis=0)

    # Compute percentage row (based on grand total)
    grand_total = summary.loc["Grand Total", "Total"]
    percentage_row = (summary.loc["Grand Total"] / grand_total * 100).round(1)

    ## Add Percentage(%) row
    summary.loc["Percentage(%)"] = percentage_row

    ## Display Reject Summary Table
    print(summary)


def display_reject_summary_table():

    ## Load data
    df = pd.read_csv(
        "./data/csv/MSR Mining Challenge 2026 Data - Manual Annotations - Reject.csv"
    )
    print("Reject Summary Table:")
    summarize_table(df)
    print("\n")


def display_approved_summary_table():

    ## Load data
    df = pd.read_csv(
        "./data/csv/MSR Mining Challenge 2026 Data - Manual Annotations - Approved.csv"
    )
    print("Approved Summary Table:")
    summarize_table(df)
    print("\n")


if __name__ == "__main__":
    display_reject_summary_table()
    display_approved_summary_table()
