import google.generativeai as genai
import time

def cro_reasoning_agent(state: dict):
    """
    CRO Reasoning Agent
    - Uses Gemini to generate CRO recommendations
    - Enforces strict CSV output
    - Enforces numeric confidence between 0 and 1
    """

    api_key = state["api_key"]
    genai.configure(api_key=api_key)

    persona = state.get("persona", "General")
    raw_data = state.get("raw_cro_data", "")
    funnel_data = state.get("funnel_text", "No funnel data provided.")
    memory_text = state.get("memory_text", "No past failed CRO ideas.")

    # 🔒 HARDENED PROMPT (THIS IS THE IMPORTANT PART)
    prompt = f"""
Act as a Senior CRO AI Agent.

TARGET PERSONA:
{persona}

WEBSITE CRO SIGNALS:
{raw_data}

FUNNEL ANALYSIS:
{funnel_data}

FAILED CRO IDEAS (avoid repeating these):
{memory_text}

TASK:
- Identify conversion friction points
- Explain the evidence briefly
- Propose high-impact CRO fixes
- Estimate expected impact

OUTPUT ONLY CSV (no markdown, no explanation, no extra text):
"URL","Issue","Evidence","Suggested Fix","Impact","Confidence"

RULES (VERY IMPORTANT):
- Confidence MUST be a decimal number between 0 and 1
- Use numeric values only (example: 0.72)
- Do NOT add words, symbols, or ranges
- Do NOT leave Confidence empty
- If unsure, use 0.5
"""

    models = [
        "gemini-2.5-flash",
        "gemini-flash-latest"
    ]

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            # Clean any accidental formatting
            csv_text = (
                response.text
                .replace("```csv", "")
                .replace("```", "")
                .strip()
            )

            state["cro_csv"] = csv_text
            return state

        except Exception:
            time.sleep(1)

    # Fallback (should rarely happen)
    state["cro_csv"] = ""
    return state
