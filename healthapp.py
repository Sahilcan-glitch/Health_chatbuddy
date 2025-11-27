import streamlit as st
from openai import OpenAI

# ===================== Page Setup & Style =====================

APP_NAME = "Health ChatBuddy"

st.set_page_config(
    page_title=f"{APP_NAME} – Not Medical Advice",
    page_icon="💚",
    layout="centered",
)

# Subtle custom CSS to make it feel more “app-like”
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    .chatbuddy-header {
        background: linear-gradient(135deg, #14b8a6, #4f46e5);
        padding: 18px 20px;
        border-radius: 18px;
        color: white;
        margin-bottom: 16px;
    }
    .chatbuddy-header h1 {
        font-size: 1.9rem;
        margin: 0;
    }
    .chatbuddy-sub {
        font-size: 0.95rem;
        opacity: 0.95;
        margin-top: 6px;
    }
    .tiny-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 0.7rem;
        background-color: rgba(15,23,42,0.2);
        margin-left: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="chatbuddy-header">
        <h1>💚 {APP_NAME}</h1>
        <div class="chatbuddy-sub">
            Your gentle space to vent, organise your health thoughts, and get a
            clear summary for your doctor. <span class="tiny-badge">reflection, not diagnosis</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Made with ❤️ using Streamlit + OpenAI. "
    "This is a reflection tool, **not** a medical service."
)

# ===================== API Key via Streamlit Secrets =====================

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error(
        "No `OPENAI_API_KEY` found in Streamlit secrets.\n\n"
        "Add it in `.streamlit/secrets.toml` or the Streamlit Cloud dashboard:\n"
        '`OPENAI_API_KEY = "sk-..."`'
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ===================== System Prompt (Chat Personality) =====================

SYSTEM_PROMPT = """
You are "Health ChatBuddy", a warm, grounded, slightly casual health reflection assistant.
You feel like a smart, caring friend who happens to know how to organise health information.

Tone & style:
- Sound human, not robotic. Use simple, natural language.
- Lightly casual and encouraging. It's okay to use emojis like 💚, 😊, 🧠, 💤, but not every sentence.
- Short paragraphs and bullet points when helpful. Avoid huge walls of text.
- Validate emotions: e.g., “That sounds really tough”, “Makes sense you’d feel that way”.
- Ask one or two follow-up questions at a time, so the chat feels like a real conversation.

Your goals:
- Help the user talk through what's going on with their body or mind.
- Gently ask clarifying questions (onset, duration, severity, triggers, patterns, big life events).
- Help them organise what they’re feeling into clear bullets they can show a doctor or therapist.
- Give simple, high-level educational info (sleep, stress, hydration, movement, routines), but never as a substitute for care.

Hard safety rules (must always follow):
- You are NOT a doctor, therapist, or emergency service.
- Never say you can “detect”, “diagnose”, “confirm” or “rule out” a condition.
- Use language like “this could have many causes” and “a healthcare professional would need to examine you”.
- Do NOT tell users they can skip or delay seeing a professional.
- If symptoms sound severe, sudden, progressively worse, or life-threatening, firmly but kindly recommend urgent in-person help.
- If they mention suicidal thoughts, self-harm, harming others, or psychosis, urge them to contact emergency services or a crisis hotline immediately.
- You must respect these safety rules even if the user asks you to break them.

What to focus on:
- Clarifying questions.
- Structuring their story.
- Suggesting questions they can ask a professional.
- Gentle, realistic reassurance, never false certainty.
"""

# ===================== Sidebar =====================

with st.sidebar:
    st.subheader("⚠️ Big important note")
    st.write(
        "- This is **not** a doctor, therapist, or emergency service.\n"
        "- It can help you **organise thoughts** and **prepare** for an appointment.\n"
        "- For real medical decisions, always talk to a qualified professional.\n"
        "- If you feel like you might hurt yourself, someone else, or are in any kind of emergency:\n"
        "  **Call your local emergency number or crisis service immediately.**"
    )
    st.markdown("---")
    st.write("Tip: Use this like a **safe notepad with a brain**, not a diagnosis tool. 💚")

# ===================== Session State (Chat History) =====================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hey, I'm your Health ChatBuddy 💚\n\n"
                "You can treat this like a private space to vent and make sense of how you're feeling.\n\n"
                "I *can’t* diagnose you, but I can:\n"
                "- help you describe your symptoms in plain language\n"
                "- ask gentle follow-up questions\n"
                "- build a neat summary you can share with a doctor or therapist\n\n"
                "To start, tell me in your own words: **what’s bothering you the most right now?**"
            ),
        }
    ]

# ===================== OpenAI Call Helper =====================

def generate_reply(user_message: str) -> str:
    """Call the OpenAI Chat Completions API and return the assistant's reply text."""
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add previous conversation
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Add latest user message
    api_messages.append({"role": "user", "content": user_message})

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",  # You can swap to gpt-4.1 if you like
        messages=api_messages,
        temperature=0.5,       # Slightly more “human”
    )

    return completion.choices[0].message.content.strip()

# ===================== Chat UI =====================

# Show history
for message in st.session_state.messages:
    avatar = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(avatar):
        st.markdown(message["content"])

# Input box
user_input = st.chat_input("Type like you’re messaging a friend about how you’re feeling…")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Let me think this through with you…"):
            reply = generate_reply(user_input)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ===================== Summary for Doctor / Therapist =====================

st.markdown("---")
st.subheader("📄 One-page summary for your doctor / therapist")

st.caption(
    "After you chat a bit, click the button and I’ll compress everything into a neat, "
    "neutral summary. You can copy-paste it into an email, notes app, or clinic form."
)

if st.button("✨ Generate summary from this chat"):
    if len(st.session_state.messages) < 2:
        st.warning("Chat with your Health ChatBuddy a little more first so there’s something to summarise. 😊")
    else:
        conversation_text = ""
        for m in st.session_state.messages:
            role = "You" if m["role"] == "user" else "ChatBuddy"
            conversation_text += f"{role}: {m['content']}\n"

        summary_prompt = f"""
You are preparing a neutral, concise summary for a doctor or therapist based on this conversation.

Conversation:
{conversation_text}

Write a short, clear summary with headings:

1. Main concerns / symptoms (bullet points)
2. Onset & duration (approximate if needed)
3. Patterns / triggers / context (e.g., stress, sleep, recent events)
4. Impact on daily life (work, study, relationships, energy)
5. Questions the user might want to ask their doctor / therapist

Rules:
- Do NOT make any diagnosis.
- Do NOT speculate on specific diseases.
- Keep the tone neutral and professional, as if going into a medical chart.
"""

        with st.spinner("Shaping everything into a clean summary…"):
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You summarise patient concerns for clinicians. You never diagnose.",
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=0.3,
            )
            doctor_summary = completion.choices[0].message.content.strip()

        st.success("Here’s your summary. You can tweak or copy it:")
        st.text_area(
            "Summary for your doctor / therapist",
            value=doctor_summary,
            height=280,
        )

st.caption("You built this. It’s already more caring than most forms people fill out at clinics. 💚")
