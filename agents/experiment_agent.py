from scipy.stats import beta
import pandas as pd

def bayesian_ab(conv_a, users_a, conv_b, users_b, samples=10000):
    a = beta.rvs(conv_a + 1, users_a - conv_a + 1, size=samples)
    b = beta.rvs(conv_b + 1, users_b - conv_b + 1, size=samples)
    return round((b > a).mean(), 3)

def experiment_agent(state: dict):
    csv_text = state.get("cro_csv", "")

    if not csv_text:
        return state

    df = pd.read_csv(
        pd.io.common.StringIO(csv_text),
        names=["URL", "Issue", "Evidence", "Suggested Fix", "Impact", "Confidence"],
        on_bad_lines="skip"
    )

    df["Confidence"] = df["Confidence"].astype(float)
    df["Effort"] = df["Suggested Fix"].apply(
        lambda x: 1 if "text" in x.lower() else 2
    )

    df["PriorityScore"] = (df["Confidence"] * 10) / df["Effort"]
    df = df.sort_values("PriorityScore", ascending=False)

    state["final_df"] = df
    return state

