import streamlit as st
import pandas as pd
from graph import build_cro_graph

st.set_page_config(page_title="AI CRO Agent", page_icon="📈", layout="wide")
st.title("📈 Autonomous AI CRO Agent")

api_key = st.text_input("🔑 Gemini API Key", type="password")
url = st.text_input("🌐 Website URL")
persona = st.selectbox(
    "👤 Persona",
    ["General", "First-time Visitor", "Returning User", "Mobile User", "B2B Decision Maker"]
)
funnel_file = st.file_uploader("📥 Funnel CSV (Optional)", type="csv")
run = st.button("🚀 Run CRO Agent", type="primary")

if run:
    if not api_key or not url:
        st.error("API key and URL are required.")
        st.stop()

    if not url.startswith("http"):
        url = "https://" + url

    graph = build_cro_graph()

    result = graph.invoke({
        "api_key": api_key,
        "url": url,
        "persona": persona,
        "funnel_file": funnel_file,
        "max_pages": 3
    })

    df = result.get("final_df")

    if df is not None:
        st.subheader("🔥 Auto-Prioritized CRO Recommendations")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "💾 Download CRO Report",
            df.to_csv(index=False),
            "cro_report.csv",
            "text/csv"
        )
    else:
        st.error("No CRO recommendations generated.")
