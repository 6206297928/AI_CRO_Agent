import pandas as pd

def funnel_agent(state: dict):
    funnel_file = state.get("funnel_file")

    if funnel_file is None:
        state["funnel_text"] = "No funnel data provided."
        return state

    df = pd.read_csv(funnel_file)
    df["drop_off"] = df["users"].shift(1) - df["users"]

    state["funnel_text"] = df.to_string(index=False)
    state["funnel_df"] = df
    return state

