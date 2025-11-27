import streamlit as st
from openai import OpenAI

# ---------- Styling ----------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
:root {
    --hb-bg: linear-gradient(135deg, #f7fbff 0%, #f4f2ff 100%);
    --hb-card: #ffffff;
    --hb-accent: #5b7cfa;
    --hb-soft: #e7edff;
    --hb-text: #1f2a44;
}
html, body, .stApp {
    background: var(--hb-bg);
    color: var(--hb-text);
    font-family: 'Manrope', 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
}
.main {
    padding-top: 1rem;
}
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(8px);
    border-right: 1px solid #e6e8f0;
}
div[data-testid="stSidebarNav"] * {
    color: var(--hb-text);
}
div.block-container {
    padding-top: 1.5rem;
}
div[data-testid="stMarkdownContainer"] p {
    font-size: 0.98rem;
}
div[data-testid="stChatMessage"] {
    background: var(--hb-card);
    border: 1px solid #e7ebf5;
    border-radius: 14px;
    padding: 0.75rem 1rem;
    box-shadow: 0 8px 24px rgba(46, 67, 152, 0.08);
}
div[data-testid="stChatMessage"]:nth-of-type(even) {
    background: #f7f9ff;
}
.stChatMessage .stMarkdown {
    font-size: 1rem;
}
.stTextInput > div > div input, .stTextArea textarea {
    border-radius: 12px;
    border: 1px solid #dbe3ff;
}
.stButton button {
    background: var(--hb-accent);
    color: #fff;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1.1rem;
    font-weight: 700;
    box-shadow: 0 8px 18px rgba(91, 124, 250, 0.25);
}
.stButton button:hover {
    background: #4968e9;
}
.stCaption, .stMarkdown small {
    color: #4a5670;
}
</style>
"""

# ---------- Page config ----------

st.set_page_config(
    page_title="Health Buddy — Warm Health Chat (Not Medical Advice)",
    page_icon="🤝",
    layout="centered",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("🤝 Health Buddy")
st.caption(
    "Gentle health chat to reflect and prep for real care. **Not medical advice.**"
)

# ---------- API key from Streamlit secrets ----------

# Make sure you set OPENAI_API_KEY in Streamlit secrets
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)

if not OPENAI_API_KEY:
    st.error(
        "No `OPENAI_API_KEY` found in Streamlit secrets.\n\n"
        "Add it in `.streamlit/secrets.toml` locally or in the Streamlit Cloud dashboard:\n"
        "`OPENAI_API_KEY = \"sk-...\"`"
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- System prompt ----------

SYSTEM_PROMPT = """
You are Health Buddy, a warm, upbeat health reflection companion (not a clinician).

What to do:
- Invite the user to share what they feel in everyday words; reflect back what you heard.
- Ask gentle, clarifying questions (onset, duration, severity, triggers, past care, meds, mood, lifestyle).
- Offer short, high-level tips about self-care, daily habits, and what to bring up with a clinician.
- Help the user prepare a concise summary or question list they can show a doctor or therapist.

Tone and style:
- Conversational, kind, and human; speak like a calm friend who knows health basics.
- Keep replies compact; use short paragraphs or light bullet points when helpful.
- Sprinkle a little warmth and encouragement (e.g., 🙌, 🌱, 😊) but no emoji spam (1-2 per response).
- Avoid jargon; explain terms in plain language if you must mention them.
- Ask one or two follow-up questions at a time.

Hard safety rules (never break these):
- You are NOT a doctor, therapist, or emergency service.
- Do NOT diagnose or say you can detect/confirm what is wrong.
- Use language like “this could have many causes” and “a healthcare professional would need to examine you.”
- Never suggest skipping or delaying professional care.
- If symptoms sound severe, sudden, worsening, or life-threatening, urge urgent in-person help.
- If suicidal thoughts, self-harm, harming others, or psychosis are mentioned, remind them to contact emergency services or a crisis hotline immediately.
- Keep your answers calm, empathetic, and clear; avoid long walls of text.
"""

# ---------- Sidebar disclaimer ----------

with st.sidebar:
    st.subheader("⚠️ Important safety note")
    st.write(
        "- Friendly guide, **not** a doctor.\n"
        "- Talk to a clinician for decisions.\n"
        "- Emergencies: call your local emergency number."
    )
    st.markdown("---")
    st.write("A gentle **journal + question helper**, not a diagnosis tool. ❤️")

# ---------- Session state for chat ----------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hey, I’m Health Buddy. 👋 Warm listener, not a doctor.\n\n"
                "Tell me what’s going on, and I’ll help you capture it and prep for a clinician.\n\n"
                "What’s bothering you most right now?"
            ),
        }
    ]

# ---------- Helper: call OpenAI chat API ----------

def generate_reply(user_message: str) -> str:
    """
    Call the OpenAI Chat Completions API with conversation history + system prompt
    and return the assistant's reply text.
    """
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add previous conversation
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Add latest user message
    api_messages.append({"role": "user", "content": user_message})

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",  # You can change model here
        messages=api_messages,
        temperature=0.4,
    )

    return completion.choices[0].message.content.strip()

# ---------- Display chat history ----------

for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "user" else "assistant"):
        st.markdown(message["content"])

# ---------- Input box ----------

user_input = st.chat_input("Share what’s on your mind or body…")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get model reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking this through with you..."):
            reply = generate_reply(user_input)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------- Extra: Summarize for your doctor ----------

st.markdown("---")
st.subheader("📝 Quick summary for your doctor")

st.caption(
    "Ready to share? I’ll draft a tight summary you can paste for your clinician."
)

if st.button("Create summary"):
    if len(st.session_state.messages) < 2:
        st.warning("Chat with the bot a bit first so there’s something to summarize.")
    else:
        conversation_text = ""
        for m in st.session_state.messages:
            role = "You" if m["role"] == "user" else "Assistant"
            conversation_text += f"{role}: {m['content']}\n"

        summary_prompt = f"""
You are preparing a neutral, concise summary for a doctor based on this conversation.

Conversation:
{conversation_text}

Write a short summary with:
- Main concerns/symptoms
- Onset and duration (approximate if needed)
- Any patterns, triggers, or important context mentioned
- How it affects daily life
- Key questions the patient might want to ask the doctor

Do NOT make any diagnosis. Just summarize.
"""

        with st.spinner("Summarizing your conversation..."):
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You summarize patient concerns for a doctor, without diagnosing.",
                    },
                    {
                        "role": "user",
                        "content": summary_prompt,
                    },
                ],
                temperature=0.3,
            )
            doctor_summary = completion.choices[0].message.content.strip()

        st.success("Here’s a summary you can copy:")
        st.text_area(
            "Summary",
            value=doctor_summary,
            height=250,
        )
