import streamlit as st
import time
import random
import requests
import io
import pandas as pd
from urllib.parse import urljoin, urlparse
import google.generativeai as genai
from bs4 import BeautifulSoup
import urllib3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI CRO Agent", page_icon="📈", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------- GEMINI CALL ----------------
def call_gemini(prompt, api_key):
    genai.configure(api_key=api_key)
    models = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-2.0-flash-lite-preview-02-05"
    ]

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            return res.text
        except Exception:
            time.sleep(2)
    return "Error: Gemini model unavailable."

# ---------------- CRO CRAWLER ----------------
@st.cache_data(show_spinner=False)
def cro_crawler(start_url, max_pages):
    visited, queue = set(), [start_url]
    base_domain = urlparse(start_url).netloc
    results = []

    progress = st.progress(0, text="🔍 Analyzing pages...")

    count = 0
    while queue and count < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5, verify=False)
            visited.add(url)

            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "lxml")

                buttons = [b.get_text(strip=True) for b in soup.find_all("button")]
                links = [a.get_text(strip=True) for a in soup.find_all("a") if len(a.get_text(strip=True)) < 30]
                forms = soup.find_all("form")

                results.append(
                    f"""
                    URL: {url}
                    BUTTONS: {buttons[:5]}
                    LINKS: {links[:5]}
                    FORMS: {len(forms)}
                    """
                )

                count += 1
                progress.progress(count / max_pages)

                for a in soup.find_all("a", href=True):
                    full = urljoin(url, a["href"])
                    if urlparse(full).netloc == base_domain and full not in visited:
                        queue.append(full)

        except Exception:
            pass

    progress.empty()
    return "\n".join(results)

# ---------------- CRO ANALYSIS ----------------
def generate_cro_report(raw_data, api_key, report_type="summary"):
    safe_data = raw_data[:12000]

    if report_type == "summary":
        prompt = f"""
        Act as a Senior CRO Specialist.

        TASK:
        - Identify conversion friction points
        - Detect CTA & UX issues
        - Explain user behavior problems

        OUTPUT:
        ### 📊 CRO Executive Summary
        - Key conversion problems
        - User psychology insights
        - High-impact recommendations

        DATA:
        {safe_data}
        """
        return call_gemini(prompt, api_key)

    else:
        prompt = f"""
        Act as a CRO Expert.

        OUTPUT ONLY CSV rows (no explanation).
        Format:
        "URL","Issue","Evidence","Suggested Fix","Impact"

        DATA:
        {safe_data}
        """
        res = call_gemini(prompt, api_key)
        return res.replace("```csv", "").replace("```", "").strip()

# ---------------- UI ----------------
st.title("📈 AI CRO Optimization Agent")
st.markdown("---")

left, right = st.columns([1, 2])

with left:
    st.info("1️⃣ Configuration")
    api_key = st.text_input("🔑 Gemini API Key", type="password")
    max_pages = st.slider("Pages to Analyze", 1, 6, 3)

with right:
    st.info("2️⃣ Website Input")
    url = st.text_input("🌐 Website URL", placeholder="https://example.com")
    run = st.button("🚀 Start CRO Analysis", type="primary")

# ---------------- EXECUTION ----------------
if run:
    if not api_key or not url:
        st.error("Please enter API key and URL.")
    else:
        if not url.startswith("http"):
            url = "https://" + url

        st.write(f"### 🔍 CRO Audit: {url}")

        data = cro_crawler(url, max_pages)

        if data:
            with st.spinner("🧠 Generating CRO Strategy..."):
                summary = generate_cro_report(data, api_key, "summary")
                st.markdown(summary)

            st.divider()

            with st.spinner("🛠️ Generating CRO Fixes..."):
                csv_data = generate_cro_report(data, api_key, "detailed")
                df = pd.read_csv(io.StringIO(csv_data),
                                 names=["URL", "Issue", "Evidence", "Suggested Fix", "Impact"],
                                 on_bad_lines="skip")

                st.dataframe(df, use_container_width=True)
                st.download_button("💾 Download CRO Report",
                                   df.to_csv(index=False),
                                   "cro_report.csv",
                                   "text/csv")
        else:
            st.error("Website blocked or no CRO data found.")
