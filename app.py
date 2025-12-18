import streamlit as st
import pandas as pd
import time
from graph import build_cro_graph

st.set_page_config(page_title="AI CRO Agent", page_icon="📈", layout="wide")
st.title("📈 Autonomous AI CRO Agent")

# ---------- USER INPUT ----------
api_key = st.text_input("🔑 Gemini API Key", type="password")
url = st.text_input("🌐 Website URL")
persona = st.selectbox(
    "👤 Persona",
    ["General", "First-time Visitor", "Returning User", "Mobile User", "B2B Decision Maker"]
)
funnel_file = st.file_uploader("📥 Funnel CSV (Optional)", type="csv")
run = st.button("🚀 Run CRO Agent", type="primary")

# ---------- RUN ----------
if run:
    if not api_key or not url:
        st.error("API key and URL are required.")
        st.stop()

    if not url.startswith("http"):
        url = "https://" + url

    # 🎯 PROGRESS UI
    progress = st.progress(0)
    status = st.empty()

    try:
        status.text("🔍 Initializing CRO Agent...")
        progress.progress(10)
        time.sleep(0.3)

        graph = build_cro_graph()

        status.text("🕷️ Analyzing website pages...")
        progress.progress(30)
        time.sleep(0.3)

        status.text("🔻 Processing funnel data...")
        progress.progress(50)
        time.sleep(0.3)

        status.text("🧠 Running CRO reasoning & AI analysis...")
        progress.progress(75)

        # 🚀 ACTUAL AGENT EXECUTION
        result = graph.invoke({
            "api_key": api_key,
            "url": url,
            "persona": persona,
            "funnel_file": funnel_file,
            "max_pages": 3
        })

        status.text("📊 Prioritizing experiments...")
        progress.progress(90)
        time.sleep(0.3)

        progress.progress(100)
        status.text("✅ CRO Analysis Complete")

    except Exception as e:
        progress.empty()
        status.empty()
        st.error("❌ Something went wrong during CRO analysis.")
        st.exception(e)
        st.stop()

    # ---------- OUTPUT ----------
    df = result.get("final_df")

    if df is not None and not df.empty:
        st.subheader("🔥 Auto-Prioritized CRO Recommendations")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "💾 Download CRO Report",
            df.to_csv(index=False),
            "cro_report.csv",
            "text/csv"
        )
    else:
        st.warning("⚠️ CRO Agent ran successfully, but no recommendations were generated.")
