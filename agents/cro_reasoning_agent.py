import google.generativeai as genai
import time

def cro_reasoning_agent(state: dict):
    genai.configure(api_key=state["api_key"])

    prompt = f"""
Act as a Senior CRO AI Agent.

TARGET PERSONA:
{state.get("persona")}

WEBSITE DATA:
{state.get("raw_cro_data")}

FUNNEL DATA:
{state.get("funnel_text")}

FAILED IDEAS (avoid repeating):
{state.get("memory_text")}

TASK:
Identify conversion friction and suggest CRO fixes.

OUTPUT ONLY CSV:
"URL","Issue","Evidence","Suggested Fix","Impact","Confidence"
"""

    models = ["gemini-2.5-flash", "gemini-flash-latest"]

    for m in models:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt)
            state["cro_csv"] = response.text.replace("```csv", "").replace("```", "").strip()
            return state
        except Exception:
            time.sleep(1)

    state["cro_csv"] = ""
    return state

