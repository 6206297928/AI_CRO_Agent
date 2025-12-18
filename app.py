import streamlit as st
import pandas as pd
import time
from graph import build_cro_graph

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI CRO Optimization Agent",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI CRO Optimization Agent")
st.markdown("---")

# ---------------- INPUT UI ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔧 Configuration")
    api_key = st.text_input("🔑 Gemini API Key", type="password")
    pages = st.slider("Pages to Analyze", 1, 6, 3)

with col2:
    st.subheader("🌐 Website Input")
    url = st.text_input("Website URL", placeholder="https://example.com")

persona = st.selectbox(
    "👤 Target Persona",
    [
        "General",
        "First-time Visitor",
        "Returning User",
        "Mobile User",
        "B2B Decision Maker"
    ]
)

funnel_file = st.file_uploader(
    "📥 Funnel CSV (Optional)",
    type="csv",
    help="Upload GA-style funnel data"
)

run = st.button("🚀 Start CRO Analysis", type="primary")

# ---------------- RUN LOGIC ----------------
if run:
    if not api_key or not url:
        st.error("❌ Please enter both API Key and Website URL.")
        st.stop()

    if not url.startswith("http"):
        url = "https://" + url

    # ---------- PROGRESS UI ----------
    progress_bar = st.progress(0)
    status = st.empty()

    try:
        status.text("🔄 Initializing CRO Agent...")
        progress_bar.progress(10)
        time.sleep(0.3)

        graph = build_cro_graph()

        status.text("🕷️ Crawling website pages...")
        progress_bar.progress(30)
        time.sleep(0.3)

        status.text("🔻 Analyzing funnel behavior...")
        progress_bar.progress(50)
        time.sleep(0.3)

        status.text("🧠 Running CRO reasoning & AI analysis...")
        progress_bar.progress(75)

        # --------- AGENT EXECUTION ---------
        result = graph.invoke({
            "api_key": api_key,
            "url": url,
            "persona": persona,
            "funnel_file": funnel_file,
            "max_pages": pages
        })

        status.text("📊 Prioritizing CRO experiments...")
        progress_bar.progress(90)
        time.sleep(0.3)

        progress_bar.progress(100)
        status.text("✅ CRO Analysis Completed")

    except Exception as e:
        progress_bar.empty()
        status.empty()
        st.error("❌ Error occurred during CRO analysis.")
        st.exception(e)
        st.stop()

    # ---------------- OUTPUT ----------------
    st.divider()

    # ---- CRO AUDIT HEADER ----
    st.markdown(f"### 🔍 CRO Audit: {url}")

    # ---- NARRATIVE SUMMARY ----
    cro_summary = result.get("cro_summary_md")
    if cro_summary:
        st.markdown(cro_summary)
    else:
        st.warning("⚠️ CRO summary could not be generated.")

    # ---- FUNNEL TABLE (OPTIONAL) ----
    funnel_df = result.get("funnel_df")
    if funnel_df is not None:
        st.divider()
        st.subheader("🔻 Funnel Analysis")
        st.dataframe(funnel_df, use_container_width=True)

    # ---- DETAILED CRO TABLE ----
    df = result.get("final_df")
    if df is not None and not df.empty:
        st.divider()
        st.subheader("📋 Detailed CRO Findings")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "💾 Download CRO Report",
            df.to_csv(index=False),
            file_name="cro_report.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No structured CRO recommendations were generated.")
