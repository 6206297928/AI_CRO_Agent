import google.generativeai as genai
import time

def cro_reasoning_agent(state: dict):
    api_key = state["api_key"]
    genai.configure(api_key=api_key)

    persona = state.get("persona", "General")
    raw_data = state.get("raw_cro_data", "")
    funnel_text = state.get("funnel_text", "No funnel data provided.")
    memory_text = state.get("memory_text", "No past failed CRO ideas.")

    # ---------- 1️⃣ NARRATIVE REPORT ----------
    narrative_prompt = f"""
Act as a Senior CRO Consultant.

TARGET PERSONA:
{persona}

WEBSITE DATA:
{raw_data}

FUNNEL INSIGHTS:
{funnel_text}

FAILED IDEAS (avoid repeating):
{memory_text}

Create a CRO report with the following sections:

### 📊 CRO Executive Summary
### 🔑 Key Conversion Problems
### 🧠 User Psychology Insights
### 🚀 High-Impact Recommendations

Use clear bullets and concise explanations.
"""

    # ---------- 2️⃣ CSV FOR EXPERIMENTS ----------
    csv_prompt = f"""
Act as a Senior CRO AI Agent.

Using the same analysis, produce ONLY a CSV table.

OUTPUT ONLY CSV (no text, no markdown):
"URL","Issue","Evidence","Suggested Fix","Impact","Confidence"

RULES:
- Confidence must be a decimal between 0 and 1
- If unsure, use 0.5
"""

    models = ["gemini-2.5-flash", "gemini-flash-latest"]

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)

            narrative_res = model.generate_content(narrative_prompt)
            csv_res = model.generate_content(csv_prompt)

            state["cro_summary_md"] = narrative_res.text.strip()
            state["cro_csv"] = (
                csv_res.text
                .replace("```csv", "")
                .replace("```", "")
                .strip()
            )
            return state

        except Exception:
            time.sleep(1)

    state["cro_summary_md"] = ""
    state["cro_csv"] = ""
    return state
