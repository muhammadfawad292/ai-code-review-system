"""
╔══════════════════════════════════════════════════════════════╗
║      AI Code Review & Converter — Powered by Gemini          ║
╚══════════════════════════════════════════════════════════════╝

INSTALLATION:
    pip install streamlit google-generativeai

HOW TO RUN:
    Option 1 — Local:
        streamlit run app.py
        (enter your API key in the sidebar input)

    Option 2 — Streamlit Community Cloud:
        Add your key to the app Secrets dashboard:
            GEMINI_API_KEY = "your_api_key_here"

GET YOUR FREE GEMINI API KEY:
    https://aistudio.google.com/app/apikey
"""

import re
import streamlit as st
import google.generativeai as genai

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Review",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — dark terminal aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #13161e;
    --border:   #1f2433;
    --green:    #00e5a0;
    --amber:    #ffb938;
    --blue:     #4da6ff;
    --purple:   #b066ff;
    --red:      #ff5f6d;
    --muted:    #5a6380;
    --text:     #d4daf0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Syne', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }
#MainMenu, footer, header { visibility: hidden; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    margin-bottom: 2.5rem;
}
.hero .badge {
    display: inline-block;
    background: #00e5a015;
    border: 1px solid #00e5a050;
    color: var(--green);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 1.1rem;
    text-transform: uppercase;
}
.hero h1 {
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    color: var(--green);
    margin: 0 0 0.5rem;
    letter-spacing: -0.01em;
    font-weight: 800;
}
.hero h1 .icon { color: #fff; margin-left: 0.3rem; font-size: 0.85em; }
.hero p {
    color: var(--muted);
    font-size: 0.95rem;
    margin: 0;
    letter-spacing: 0.02em;
}
.hero p span { margin: 0 0.4rem; opacity: 0.4; }

/* ── Two-column wrapper ── */
.main-layout {
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 2rem;
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 1.5rem 3rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    color: var(--muted);
    text-transform: uppercase;
    margin: 1.4rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Left panel heading ── */
.panel-heading {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Cards ── */
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
.card.green  .card-header { color: var(--green);  border-color: #00e5a030; }
.card.amber  .card-header { color: var(--amber);  border-color: #ffb93830; }
.card.blue   .card-header { color: var(--blue);   border-color: #4da6ff30; }
.card.purple .card-header { color: var(--purple); border-color: #b066ff30; }

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
.card .prose { font-size: 0.93rem; line-height: 1.75; color: var(--text); }
.card .prose ul { padding-left: 1.4rem; margin: 0.5rem 0; }
.card .prose li { margin-bottom: 0.35rem; }

/* ── Textarea ── */
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
[data-testid="stTextArea"] label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    color: var(--muted) !important;
    text-transform: uppercase;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--green) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.04em !important;
    transition: opacity 0.15s ease, transform 0.1s ease !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── Convert button — purple accent ── */
.convert-btn .stButton > button {
    background: var(--green) !important;
    color: #0d0f14 !important;
}

/* ── Divider ── */
.panel-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Convert section sub-caption ── */
.convert-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin: -0.4rem 0 1rem;
    letter-spacing: 0.02em;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #090b11 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}
[data-testid="stSelectbox"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
}

/* ── Text input (API key) ── */
[data-testid="stTextInput"] input {
    background: #090b11 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Results panel heading ── */
.results-heading {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Info box ── */
.info-box {
    background: #131926;
    border: 1px solid #1f2d45;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    font-size: 0.88rem;
    color: var(--text);
}
.info-box .icon { font-size: 1rem; margin-top: 0.05rem; }
.info-box strong { color: #fff; }

/* ── Misc ── */
.stAlert { border-radius: 8px !important; border-left-width: 3px !important; }
[data-testid="stSpinner"] p { color: var(--green) !important; }
hr { border-color: var(--border) !important; }

/* Tighten Streamlit column gaps to match layout */
[data-testid="stHorizontalBlock"] {
    gap: 2rem !important;
    align-items: flex-start !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LANGUAGE MAPPINGS
# ─────────────────────────────────────────────

LANG_MAP: dict = {
    "Python":     "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java":       "java",
    "C++":        "cpp",
    "C":          "c",
    "C#":         "csharp",
    "Go":         "go",
    "Rust":       "rust",
    "Kotlin":     "kotlin",
    "Swift":      "swift",
    "Ruby":       "ruby",
    "PHP":        "php",
    "SQL":        "sql",
    "Bash":       "bash",
    "Dart":       "dart",
    "Scala":      "scala",
    "R":          "r",
}

LANG_ALIAS: dict = {
    "python": "Python", "javascript": "JavaScript", "js": "JavaScript",
    "typescript": "TypeScript", "ts": "TypeScript", "java": "Java",
    "c++": "C++", "cpp": "C++", "c": "C", "c#": "C#", "csharp": "C#",
    "go": "Go", "golang": "Go", "rust": "Rust", "kotlin": "Kotlin",
    "swift": "Swift", "ruby": "Ruby", "php": "PHP", "sql": "SQL",
    "bash": "Bash", "shell": "Bash", "sh": "Bash",
    "dart": "Dart", "scala": "Scala", "r": "R",
}

CONVERT_TARGETS = list(LANG_MAP.keys())


# ─────────────────────────────────────────────
#  PROMPTS
# ─────────────────────────────────────────────
REVIEW_PROMPT = """You are an expert code reviewer. Analyze the following code carefully.

Return your response in EXACTLY this format (use these exact section headers):

## DETECTED_LANGUAGE
<write only the programming language name, e.g. Python, JavaScript, Java, C++. One short name only.>

## CORRECTED_CODE
```
<paste the full corrected code here>
```

## BUG_EXPLANATION
<explain each bug found, what caused it, and how the fix resolves it. Use bullet points.>

## SUGGESTIONS
<list best practices, improvements, or optimizations. Use bullet points.>

Code to review:

{user_code}
"""

CONVERT_PROMPT = """You are an expert polyglot software engineer.
Convert the following {source_lang} code to idiomatic {target_lang}.
Preserve all logic exactly. Use {target_lang} conventions, idioms, and standard libraries.

Return your response in EXACTLY this format (use these exact section headers):

## CONVERTED_CODE
```
<full converted {target_lang} code here>
```

## CONVERSION_NOTES
<explain key differences that affected the conversion: type systems, memory model, library substitutions, syntax changes, etc. Use bullet points.>

## BEST_PRACTICES
<list {target_lang}-specific best practices and idioms applied or recommended. Use bullet points.>

{source_lang} code to convert:

{user_code}
"""


# ─────────────────────────────────────────────
#  GEMINI HELPERS
# ─────────────────────────────────────────────
def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def call_gemini(model, prompt: str) -> str:
    return model.generate_content(prompt).text


def detect_language(model, code: str) -> str:
    raw = call_gemini(
        model,
        f"What programming language is this code written in? "
        f"Reply with ONLY the language name (e.g. Python, C++, Java). No extra text.\n\n{code}"
    ).strip().splitlines()[0].strip()
    return LANG_ALIAS.get(raw.lower(), raw)


# ─────────────────────────────────────────────
#  PARSERS
# ─────────────────────────────────────────────
def _extract_code_block(raw: str, header: str, next_header: str = "") -> str:
    pattern = rf"##\s*{re.escape(header)}\s*```(?:\w+)?\n?(.*?)```"
    m = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    if next_header:
        fallback = re.search(
            rf"##\s*{re.escape(header)}\s*(.*?)##\s*{re.escape(next_header)}",
            raw, re.DOTALL | re.IGNORECASE,
        )
        if fallback:
            return fallback.group(1).strip()
    return f"(No {header.lower().replace('_', ' ')} returned)"


def _extract_section(raw: str, header: str, next_header: str = "") -> str:
    end = rf"(?:##\s*{re.escape(next_header)}|$)" if next_header else r"$"
    m = re.search(
        rf"##\s*{re.escape(header)}\s*(.*?){end}",
        raw, re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else f"(No {header.lower().replace('_', ' ')} returned)"


def parse_review(raw: str) -> dict:
    sections = {}
    lang_m = re.search(r"##\s*DETECTED_LANGUAGE\s*\n(.+?)(?=\n##|\Z)", raw, re.DOTALL | re.IGNORECASE)
    raw_lang = lang_m.group(1).strip().splitlines()[0].strip() if lang_m else "Unknown"
    sections["detected_language"] = LANG_ALIAS.get(raw_lang.lower(), raw_lang)
    sections["corrected_code"]    = _extract_code_block(raw, "CORRECTED_CODE", "BUG_EXPLANATION")
    sections["bug_explanation"]   = _extract_section(raw, "BUG_EXPLANATION", "SUGGESTIONS")
    sections["suggestions"]       = _extract_section(raw, "SUGGESTIONS")
    return sections


def parse_conversion(raw: str) -> dict:
    sections = {}
    sections["converted_code"]   = _extract_code_block(raw, "CONVERTED_CODE", "CONVERSION_NOTES")
    sections["conversion_notes"] = _extract_section(raw, "CONVERSION_NOTES", "BEST_PRACTICES")
    sections["best_practices"]   = _extract_section(raw, "BEST_PRACTICES")
    return sections


# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def render_card(color: str, icon: str, title: str, content: str, is_code: bool = False):
    inner = f"<pre>{content}</pre>" if is_code else f'<div class="prose">{content}</div>'
    st.markdown(f"""
    <div class="card {color}">
        <div class="card-header">{icon}&nbsp; {title}</div>
        {inner}
    </div>
    """, unsafe_allow_html=True)


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out, in_list = [], False
    for line in lines:
        s = line.strip()
        if s.startswith(("- ", "* ", "• ")):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{s[2:].strip()}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if s:
                out.append(f"<p>{s}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def to_st_lang(display: str) -> str:
    return LANG_MAP.get(display, "text")


def show_api_error(exc: Exception):
    msg = str(exc)
    if "API_KEY_INVALID" in msg or "invalid" in msg.lower():
        st.error("🔑 Invalid API key. Please check your Gemini API key and try again.")
    elif "quota" in msg.lower() or "429" in msg:
        st.error("🚦 Rate limit reached. Please wait a moment and try again.")
    elif "network" in msg.lower() or "connection" in msg.lower():
        st.error("🌐 Network error. Please check your internet connection.")
    else:
        st.error(f"❌ An error occurred:\n\n```\n{msg}\n```")


def validate(api_key: str, code: str) -> str | None:
    if not api_key.strip():
        return "❌ Please enter your Gemini API key."
    if not code.strip():
        return "⚠️ Code input is empty. Please paste some code."
    if len(code.strip()) < 5:
        return "⚠️ Code is too short. Please paste a meaningful snippet."
    return None


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Hero ─────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
        <div class="badge">Made by Muhammad Fawad</div>
        <h1>AI Code Audit System <span class="icon">∞</span></h1>
        <p>Review bugs <span>·</span> Fix code <span>·</span> Convert between languages — instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout: narrow left, wide right ────────────
    left, right = st.columns([1, 1.6], gap="large")

    # ════════════════════════════════════
    #  LEFT PANEL
    # ════════════════════════════════════
    with left:
        api_key = st.secrets.get("GEMINI_API_KEY", "")

        # ── Your Code heading ──
        st.markdown('<div class="panel-heading">📝 Your Code</div>', unsafe_allow_html=True)

        user_code = st.text_area(
            label="PASTE CODE BELOW",
            placeholder=(
                "# Paste any code here — Python, JS, Java, C++, SQL, etc.\n\n"
                "def greet(name):\n    print('Hello, ' + name)\n\ngreet()"
            ),
            height=280,
            key="code_input",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Review Button ─────────────────────────────────────
        review_clicked = st.button("🔍  Review Code", use_container_width=True, key="btn_review")

        # ── Divider ──────────────────────────────────────────
        st.markdown('<hr class="panel-divider">', unsafe_allow_html=True)

        # ── Convert Section ───────────────────────────────────
        st.markdown('<div class="panel-heading">🔄 Convert Language</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="convert-caption">CodeAudit auto-detects your source language. Choose the target below.</p>',
            unsafe_allow_html=True
        )

        target_lang = st.selectbox(
            label="CONVERT TO",
            options=CONVERT_TARGETS,
            index=0,
            key="target_lang",
            help="Pick the language you want your code translated into.",
        )

        st.markdown('<div class="convert-btn">', unsafe_allow_html=True)
        convert_clicked = st.button("⚡  Convert Code", use_container_width=True, key="btn_convert")
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════
    #  RIGHT PANEL
    # ════════════════════════════════════
    with right:

        if not review_clicked and not convert_clicked:
            st.markdown('<div class="results-heading">📊 Results</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="info-box">
                <span class="icon">👉</span>
                <span>Paste your code on the left, then click <strong>Review Code</strong> or <strong>Convert Code</strong>.</span>
            </div>
            """, unsafe_allow_html=True)
            return

        # ────────────────────────────────
        #  REVIEW MODE
        # ────────────────────────────────
        if review_clicked:
            st.markdown('<div class="results-heading">📊 Review Results</div>', unsafe_allow_html=True)

            with st.spinner("🤖 CodeAudit is reviewing your code…"):
                try:
                    model   = get_model(api_key.strip())
                    raw     = call_gemini(model, REVIEW_PROMPT.format(user_code=user_code.strip()))
                    results = parse_review(raw)
                except Exception as exc:
                    show_api_error(exc)
                    return

            detected = results["detected_language"]
            st_lang  = to_st_lang(detected)

            render_card("green", "✅", f"Corrected Code ({detected})",
                        results["corrected_code"], is_code=True)
            st.code(results["corrected_code"], language=st_lang)
            st.caption("☝️ Use the copy icon above to copy the corrected code.")

            render_card("amber", "🧠", "Bug Explanation",
                        md_to_html(results["bug_explanation"]))

            render_card("blue", "💡", "Suggestions & Best Practices",
                        md_to_html(results["suggestions"]))

            st.success("✅ Review complete!")

        # ────────────────────────────────
        #  CONVERT MODE
        # ────────────────────────────────
        elif convert_clicked:
            st.markdown('<div class="results-heading">📊 Conversion Results</div>', unsafe_allow_html=True)

            with st.spinner("🔎 Detecting source language…"):
                try:
                    model       = get_model(api_key.strip())
                    source_lang = detect_language(model, user_code.strip())
                except Exception as exc:
                    show_api_error(exc)
                    return

            if source_lang.lower() == target_lang.lower():
                st.warning(
                    f"⚠️ Source is already **{source_lang}**. "
                    f"Please choose a different target language."
                )
                return

            st.markdown(
                f'<div class="section-label">Converting {source_lang} → {target_lang}</div>',
                unsafe_allow_html=True,
            )

            with st.spinner(f"⚡ Converting {source_lang} → {target_lang}…"):
                try:
                    conv_raw = call_gemini(
                        model,
                        CONVERT_PROMPT.format(
                            source_lang=source_lang,
                            target_lang=target_lang,
                            user_code=user_code.strip(),
                        ),
                    )
                    conv = parse_conversion(conv_raw)
                except Exception as exc:
                    show_api_error(exc)
                    return

            st_lang = to_st_lang(target_lang)

            render_card("purple", "⚡", f"Converted Code ({target_lang})",
                        conv["converted_code"], is_code=True)
            st.code(conv["converted_code"], language=st_lang)
            st.caption("☝️ Use the copy icon above to copy the converted code.")

            render_card("amber", "🧠",
                        f"Conversion Notes  ({source_lang} → {target_lang})",
                        md_to_html(conv["conversion_notes"]))

            render_card("blue", "💡",
                        f"Best Practices ({target_lang})",
                        md_to_html(conv["best_practices"]))

            st.success(f"✅ Conversion complete — {source_lang} → {target_lang}!")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
