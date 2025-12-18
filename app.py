import streamlit as st
import time
import requests
import io
import os
import pandas as pd
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib3

# ===== VECTOR MEMORY =====
import faiss
import numpy as np

# ================= CONFIG =================
st.set_page_config(page_title="AI CRO Agent", page_icon="📈", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MEMORY_INDEX = "cro_memory.index"
MEMORY_META = "cro_memory.csv"

# ================= GEMINI =================
def call_gemini(prompt, api_key):
    genai.configure(api_key=api_key)
    models = ["gemini-2.5-flash", "gemini-flash-latest"]

    for m in models:
        try:
            model = genai.GenerativeModel(m)
            return model.generate_content(prompt).text
        except Exception:
            time.sleep(1)
    return ""

# ============== EMBEDDINGS ==============
def embed_text(text, api_key):
    genai.configure(api_key=api_key)
    emb = genai.embed_content(
        model="models/embedding-001",
        content=text
    )
    return np.array(emb["embedding"]).astype("float32")

# ============== VECTOR MEMORY ==============
def load_vector_db(dim=768):
    if os.path.exists(MEMORY_INDEX):
        return faiss.read_index(MEMORY_INDEX)
    return faiss.IndexFlatL2(dim)

def save_vector_db(index):
    faiss.write_index(index, MEMORY_INDEX)

def load_memory_meta():
    if os.path.exists(MEMORY_META):
        return pd.read_csv(MEMORY_META)
    return pd.DataFrame(columns=["issue", "fix", "outcome"])

def store_failed_idea(issue, fix, api_key):
    vec = embed_text(issue + " " + fix, api_key)
    index = load_vector_db(len(vec))
    index.add(vec.reshape(1, -1))
    save_vector_db(index)

    meta = load_memory_meta()
    meta.loc[len(meta)] = [issue, fix, "failed"]
    meta.to_csv(MEMORY_META, index=False)

def retrieve_failed_ideas(query, api_key, top_k=3):
    if not os.path.exists(MEMORY_INDEX):
        return ""

    vec = embed_text(query, api_key)
    index = load_vector_db(len(vec))
    D, I = index.search(vec.reshape(1, -1), top_k)

    meta = load_memory_meta()
    results = meta.iloc[I[0]] if len(meta) > 0 else []
    return results.to_string(index=False)

# ============== CRO CRAWLER ==============
@st.cache_data(show_spinner=False)
def cro_crawler(start_url, max_pages):
    visited, queue = set(), [start_url]
    base = urlparse(start_url).netloc
    data = []

    bar = st.progress(0, text="🔍 Analyzing pages...")
    count = 0

    while queue and count < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
            visited.add(url)

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                buttons = [b.get_text(strip=True) for b in soup.find_all("button")]
                forms = len(soup.find_all("form"))

                data.append(
                    f"URL:{url} | BUTTONS:{buttons[:5]} | FORMS:{forms}"
                )

                count += 1
                bar.progress(count / max_pages)

                for a in soup.find_all("a", href=True):
                    link = urljoin(url, a["href"])
                    if urlparse(link).netloc == base and link not in visited:
                        queue.append(link)
        except Exception:
            pass

    bar.empty()
    return "\n".join(data)

# ============== FUNNEL PARSER ==============
def parse_funnel(csv_file):
    df = pd.read_csv(csv_file)
    df["drop_off"] = df["users"].shift(1) - df["users"]
    return df

# ============== A/B TEST INGESTION ==============
def parse_ab_test(csv_file):
    """
    Expected format:
    variant,conversions,users
    A,120,1000
    B,160,1000
    """
    df = pd.read_csv(csv_file)
    df["conversion_rate"] = df["conversions"] / df["users"]
    return df

# ============== CRO REPORT ==============
def generate_cro_report(raw, funnel, persona, api_key):
    failed_memory = retrieve_failed_ideas(raw[:500], api_key)

    prompt = f"""
Act as a Senior CRO AI Agent.

TARGET PERSONA: {persona}

AVAILABLE DATA:
Website CRO Signals:
{raw}

Funnel Analysis:
{funnel}

FAILED IDEAS MEMORY (avoid repeating):
{failed_memory}

TASK:
1. Identify conversion friction
2. Propose CRO fixes
3. Assign confidence score (0–1)

OUTPUT ONLY CSV:
"URL","Issue","Evidence","Suggested Fix","Impact","Confidence"
"""
    return call_gemini(prompt, api_key).replace("```csv", "").replace("```", "").strip()

# ================= UI =================
st.title("📈 AI CRO Agent (Autonomous)")
st.markdown("---")

left, right = st.columns([1, 2])

with left:
    api_key = st.text_input("🔑 Gemini API Key", type="password")
    pages = st.slider("Pages to Analyze", 1, 6, 3)
    persona = st.selectbox(
        "👤 Persona",
        ["General", "First-time Visitor", "Returning User", "Mobile User", "B2B Decision Maker"]
    )

with right:
    url = st.text_input("🌐 Website URL")
    funnel_file = st.file_uploader("📥 Funnel CSV (Optional)", type="csv")
    ab_file = st.file_uploader("🧪 A/B Test Results (Optional)", type="csv")
    run = st.button("🚀 Run CRO Agent", type="primary")

# ================= RUN =================
if run:
    if not api_key or not url:
        st.error("API key and URL required.")
        st.stop()

    if not url.startswith("http"):
        url = "https://" + url

    st.write(f"### 🔍 CRO Audit: {url}")

    raw_data = cro_crawler(url, pages)

    funnel_txt = ""
    if funnel_file:
        funnel_df = parse_funnel(funnel_file)
        st.subheader("🔻 Funnel Analysis")
        st.dataframe(funnel_df)
        funnel_txt = funnel_df.to_string(index=False)

    if ab_file:
        ab_df = parse_ab_test(ab_file)
        st.subheader("🧪 A/B Test Results")
        st.dataframe(ab_df)

        # Save failed variant to memory
        loser = ab_df.sort_values("conversion_rate").iloc[0]
        store_failed_idea("A/B Test Variant Failure", str(loser.to_dict()), api_key)

    with st.spinner("🧠 Reasoning & Optimization..."):
        csv = generate_cro_report(raw_data, funnel_txt, persona, api_key)

        df = pd.read_csv(
            io.StringIO(csv),
            names=["URL", "Issue", "Evidence", "Suggested Fix", "Impact", "Confidence"],
            on_bad_lines="skip"
        )

        st.subheader("📊 CRO Recommendations")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "💾 Download CRO Report",
            df.to_csv(index=False),
            "cro_report.csv",
            "text/csv"
        )

    with st.expander("🧠 Failed Ideas Memory (Vector DB)"):
        st.dataframe(load_memory_meta())
