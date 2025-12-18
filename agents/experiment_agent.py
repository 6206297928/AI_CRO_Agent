from scipy.stats import beta
import pandas as pd

def experiment_agent(state: dict):
    csv_text = state.get("cro_csv", "")

    if not csv_text.strip():
        state["final_df"] = None
        return state

    df = pd.read_csv(
        pd.io.common.StringIO(csv_text),
        names=["URL", "Issue", "Evidence", "Suggested Fix", "Impact", "Confidence"],
        on_bad_lines="skip"
    )

    # 🔒 Robust confidence parsing (FIX)
    df["Confidence"] = (
        df["Confidence"]
        .astype(str)
        .str.extract(r"([0-9]*\.?[0-9]+)")
        .astype(float)
    )

    df["Confidence"] = df["Confidence"].fillna(0.5)

    # Simple effort heuristic
    df["Effort"] = df["Suggested Fix"].astype(str).apply(
        lambda x: 1 if any(k in x.lower() for k in ["text", "copy", "cta"]) else 2
    )

    # Priority score
    df["PriorityScore"] = (df["Confidence"] * 10) / df["Effort"]
    df = df.sort_values("PriorityScore", ascending=False)

    state["final_df"] = df
    return state
