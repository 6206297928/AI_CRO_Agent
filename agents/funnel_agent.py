import pandas as pd

def funnel_agent(state: dict):
    funnel_file = state.get("funnel_file")

    if funnel_file is None:
        state["funnel_text"] = "No funnel data provided."
        state["funnel_df"] = None
        return state

    df = pd.read_csv(funnel_file)
    df["drop_off"] = df["users"].shift(1) - df["users"]

    insights = []

    for i in range(1, len(df)):
        prev_step = df.iloc[i - 1]["step_name"]
        curr_step = df.iloc[i]["step_name"]
        prev_users = df.iloc[i - 1]["users"]
        curr_users = df.iloc[i]["users"]

        drop_pct = round(((prev_users - curr_users) / prev_users) * 100, 1)

        insights.append(
            f"{drop_pct}% users drop from '{prev_step}' to '{curr_step}'."
        )

    # 🔥 THIS is what Gemini needs
    state["funnel_text"] = " ".join(insights)

    # Table is still kept for UI
    state["funnel_df"] = df

    return state
