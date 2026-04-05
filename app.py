"""
╔══════════════════════════════════════════════════════════════╗
║           AI Code Review System — Powered by Gemini          ║
╚══════════════════════════════════════════════════════════════╝

INSTALLATION:
    pip install streamlit google-generativeai

HOW TO RUN:
    Option 1 — Local:
        export GEMINI_API_KEY="your_api_key_here"   # Linux/Mac
        set GEMINI_API_KEY=your_api_key_here         # Windows CMD
        streamlit run app.py

    Option 2 — Google Colab:
        !pip install streamlit google-generativeai pyngrok -q
        from google.colab import userdata
        import os
        os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")
        # Then run:  !streamlit run app.py &
        # And use ngrok to expose the port

GET YOUR FREE GEMINI API KEY:
    → https://aistudio.google.com/app/apikey
"""

import os
import re
import streamlit as st
# import google.genai as genai
import google.generativeai as genai

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Review",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  — dark terminal aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap');

/* ── Root variables ── */
:root {
    --bg:       #0d0f14;
    --surface:  #13161e;
    --border:   #1f2433;
    --green:    #00e5a0;
    --amber:    #ffb938;
    --blue:     #4da6ff;
    --red:      #ff5f6d;
    --muted:    #5a6380;
    --text:     #d4daf0;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Syne', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.hero .badge {
    display: inline-block;
    background: #00e5a020;
    border: 1px solid var(--green);
    color: var(--green);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero h1 {
    font-size: clamp(2rem, 5vw, 3.2rem);
    color: #fff;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.hero h1 span { color: var(--green); }
.hero p {
    color: var(--muted);
    font-size: 1.05rem;
    margin: 0;
}

/* ── Section cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}
.card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--border);
}

/* ── Section accent colours ── */
.card.green .card-header { color: var(--green); border-color: #00e5a030; }
.card.amber .card-header { color: var(--amber); border-color: #ffb93830; }
.card.blue  .card-header { color: var(--blue);  border-color: #4da6ff30; }

/* ── Code block inside card ── */
.card pre {
    background: #090b11 !important;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    overflow-x: auto;
    color: #c9d1e8;
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0;
}

/* ── Prose inside card ── */
.card .prose {
    font-size: 0.93rem;
    line-height: 1.75;
    color: var(--text);
}
.card .prose ul { padding-left: 1.4rem; margin: 0.5rem 0; }
.card .prose li { margin-bottom: 0.35rem; }

/* ── Streamlit text_area ── */
textarea {
    background: #090b11 !important;
    color: #c9d1e8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    caret-color: var(--green) !important;
}
textarea:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px #00e5a015 !important;
}

/* ── Label above textarea ── */
[data-testid="stTextArea"] label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    color: var(--muted) !important;
}

/* ── Primary button ── */
.stButton > button {
    background: var(--green) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2.2rem !important;
    letter-spacing: 0.04em !important;
    transition: opacity 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── API key input ── */
[data-testid="stTextInput"] input {
    background: #090b11 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Alert / info boxes ── */
.stAlert {
    border-radius: 8px !important;
    border-left-width: 3px !important;
}

/* ── Spinner text ── */
[data-testid="stSpinner"] p { color: var(--green) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Copy area ── */
.copy-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
MODEL_NAME = "models/gemini-2.5-flash"        # Free-tier, fast

REVIEW_PROMPT = """You are an expert code reviewer. Analyze the following code carefully.

Return your response in EXACTLY this format (use these exact section headers):

## CORRECTED_CODE
```
<paste the full corrected code here>
```

## BUG_EXPLANATION
<explain each bug found, what caused it, and how the fix resolves it. Use bullet points.>

## SUGGESTIONS
<list best practices, improvements, or optimizations the developer should adopt. Use bullet points.>

Now review this code:

{user_code}
"""


# ─────────────────────────────────────────────
#  HELPER: configure Gemini and get client
# ─────────────────────────────────────────────
def get_gemini_client():
    """Configure Gemini using Streamlit secrets and return model."""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel(MODEL_NAME)


# ─────────────────────────────────────────────
#  HELPER: call Gemini API
# ─────────────────────────────────────────────
def review_code(model, user_code: str) -> str:
    """
    Send the user's code to Gemini for review.
    Returns the raw text response from the model.
    Raises an exception on API failure.
    """
    prompt = REVIEW_PROMPT.format(user_code=user_code)
    response = model.generate_content(prompt)
    return response.text


# ─────────────────────────────────────────────
#  HELPER: parse Gemini response into sections
# ─────────────────────────────────────────────
def parse_response(raw: str) -> dict:
    """
    Extract the three sections from the model's structured response.
    Returns a dict with keys: corrected_code, bug_explanation, suggestions.
    Falls back gracefully if parsing fails.
    """
    sections = {"corrected_code": "", "bug_explanation": "", "suggestions": ""}

    # ── Corrected code block ──────────────────────
    code_match = re.search(
        r"##\s*CORRECTED_CODE\s*```(?:\w+)?\n?(.*?)```",
        raw, re.DOTALL | re.IGNORECASE
    )
    if code_match:
        sections["corrected_code"] = code_match.group(1).strip()
    else:
        # Fallback: grab anything between CORRECTED_CODE and BUG_EXPLANATION
        fallback = re.search(
            r"##\s*CORRECTED_CODE\s*(.*?)##\s*BUG_EXPLANATION",
            raw, re.DOTALL | re.IGNORECASE
        )
        sections["corrected_code"] = fallback.group(1).strip() if fallback else "(No corrected code returned)"

    # ── Bug explanation ───────────────────────────
    bug_match = re.search(
        r"##\s*BUG_EXPLANATION\s*(.*?)(?:##\s*SUGGESTIONS|$)",
        raw, re.DOTALL | re.IGNORECASE
    )
    sections["bug_explanation"] = bug_match.group(1).strip() if bug_match else "(No explanation returned)"

    # ── Suggestions ───────────────────────────────
    sug_match = re.search(
        r"##\s*SUGGESTIONS\s*(.*?)$",
        raw, re.DOTALL | re.IGNORECASE
    )
    sections["suggestions"] = sug_match.group(1).strip() if sug_match else "(No suggestions returned)"

    return sections


# ─────────────────────────────────────────────
#  HELPER: render a result card
# ─────────────────────────────────────────────
def render_card(color: str, icon: str, title: str, content: str, is_code: bool = False):
    """Render a styled result card using raw HTML."""
    inner = f"<pre>{content}</pre>" if is_code else f'<div class="prose">{content}</div>'
    st.markdown(f"""
    <div class="card {color}">
        <div class="card-header">{icon} {title}</div>
        {inner}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Hero header ──────────────────────────
    st.markdown("""
    <div class="hero">
            <div class="badge">Made by Muhammad Fawad</div>
       <!-- <div class="badge">POWERED BY GEMINI 1.5 FLASH</div> -->
        <h1>AI <span>Code Review</span> System</h1>
        <p>Paste your code → get bugs fixed, explained, and improved instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Layout: left panel (inputs) | right panel (output) ──
    left, right = st.columns([1, 1.3], gap="large")

    with left:
        # Check if secret exists
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("❌ API key not configured. Please add it in Streamlit secrets.")
            st.stop()
        # if not env_key:
        #     st.caption("🔑 Set `GEMINI_API_KEY` env variable to skip this step.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📝 Your Code")

        # Code input area
        user_code = st.text_area(
            label="PASTE CODE BELOW",
            placeholder="# Paste any code here — Python, JS, Java, C++, SQL, etc.\n\ndef greet(name):\n    print('Hello, ' + name)\n\ngreet()",
            height=380,
            key="code_input",
        )

        # Review button
        review_clicked = st.button("🔍  Review Code", use_container_width=True)

    # ── Right panel: results ──────────────────
    with right:
        st.markdown("#### 📊 Review Results")

        if not review_clicked:
            st.info("👈  Paste your code on the left and click **Review Code** to get started.")
            return

        # ── Validation ───────────────────────
        # if not api_key.strip():
        #     st.error("❌ Please enter your Gemini API key.")
        #     return

        if not user_code.strip():
            st.warning("⚠️  Code input is empty. Please paste some code to review.")
            return

        if len(user_code.strip()) < 5:
            st.warning("⚠️  Code is too short to review. Please paste a meaningful snippet.")
            return

        # ── Call Gemini ───────────────────────
        with st.spinner("🤖 Gemini is reviewing your code…"):
            try:
                model = get_gemini_client()
                raw     = review_code(model, user_code.strip())
                results = parse_response(raw)
            except Exception as exc:
                error_msg = str(exc)
                if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                    st.error("🔑 Invalid API key. Please check your Gemini API key and try again.")
                elif "quota" in error_msg.lower() or "429" in error_msg:
                    st.error("🚦 Rate limit reached. Please wait a moment and try again.")
                elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                    st.error("🌐 Network error. Please check your internet connection.")
                else:
                    st.error(f"❌ An error occurred:\n\n```\n{error_msg}\n```")
                return

        # ── Render the three result cards ─────
        render_card(
            color="green",
            icon="✅",
            title="Corrected Code",
            content=results["corrected_code"],
            is_code=True,
        )

        # Copy-to-clipboard button for corrected code
        st.code(results["corrected_code"], language="python")   # hidden native code block for easy copy
        st.caption("☝️ Use the copy icon above to copy the corrected code.")

        # Convert markdown-style bullets to HTML for prose sections
        def md_to_html_bullets(text: str) -> str:
            """Convert markdown bullet lines to HTML list items."""
            lines = text.split("\n")
            html_lines, in_list = [], False
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(("- ", "* ", "• ")):
                    if not in_list:
                        html_lines.append("<ul>")
                        in_list = True
                    html_lines.append(f"<li>{stripped[2:].strip()}</li>")
                else:
                    if in_list:
                        html_lines.append("</ul>")
                        in_list = False
                    if stripped:
                        html_lines.append(f"<p>{stripped}</p>")
            if in_list:
                html_lines.append("</ul>")
            return "\n".join(html_lines)

        render_card(
            color="amber",
            icon="🧠",
            title="Bug Explanation",
            content=md_to_html_bullets(results["bug_explanation"]),
        )

        render_card(
            color="blue",
            icon="💡",
            title="Suggestions & Best Practices",
            content=md_to_html_bullets(results["suggestions"]),
        )

        st.success("✅ Review complete! Scroll up to see all sections.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
