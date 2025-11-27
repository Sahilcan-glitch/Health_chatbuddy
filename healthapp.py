
---

## 3. `app.py`

```python
import os
from dotenv import load_dotenv

import streamlit as st
from openai import OpenAI

# ---------- Setup ----------

load_dotenv()  # Load variables from .env if present

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="Health Reflection Chatbot (Not Medical Advice)",
    page_icon="🩺",
    layout="centered",
)

st.title("🩺 Health Reflection Chatbot")
st.caption(
    "A supportive chatbot to help you reflect on your symptoms and concerns. "
    "**This is NOT medical advice or a diagnosis tool.**"
)

# Safety: stop if no API key
if not OPENAI_API_KEY:
    st.error(
        "No `OPENAI_API_KEY` found.\n\n"
        "Create a `.env` file or set the environment variable before running:\n"
        "`OPENAI_API_KEY=your_key_here`"
    )
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a supportive, non-judgmental health reflection assistant.

Your goals:
- Help the user describe their symptoms, feelings, and concerns in a structured way.
- Ask gentle, clarifying questions (e.g., onset, duration, severity, triggers, medical history).
- Help the user prepare questions and a summary they can share with a doctor or mental health professional.
- Provide general, educational information (e.g., lifestyle habits, stress, sleep), but keep it high-level.

Hard safety rules:
- You are NOT a doctor, therapist, or emergency service.
- You MUST NOT diagnose or name a specific condition as if you are sure.
- Do NOT say that you can “detect” or “confirm” what is wrong.
- Use language like “this could have many causes” and “a healthcare professional would need to examine you.”
- Never tell the user they can skip or delay seeing a professional.
- If the user’s symptoms sound severe, sudden, getting worse, or life-threatening, urge them to seek urgent in-person help.
- If they mention suicidal thoughts, self-harm, harming others, or psychosis, remind them to contact emergency services or a crisis hotline immediately.
- Keep your answers calm, empathetic, and clear; avoid long walls of text.

Style:
- Warm, validating, and concise.
- Ask one or two follow-up questions at a time.
- Avoid medical jargon when possible.
"""

# ---------- Sidebar disclaimer ----------

with st.sidebar:
    st.subheader("⚠️ Important safety note")
    st.write(
        "- This chatbot **cannot** diagnose or treat any condition.\n"
        "- Always consult a **doctor or mental health professional** for medical decisions.\n"
        "- If you have chest pain, difficulty breathing, feel you might hurt yourself or others, "
        "or any other emergency: **call your local emergency number immediately.**"
    )
    st.markdown("---")
    st.write("Use this tool like a **journal + question helper**, not a doctor. ❤️")

# ---------- Session state for chat ----------

if "messages" not in st.session_state:
    # Store only user/assistant messages here (no system message)
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I'm your health reflection buddy. 👋\n\n"
                "I can't diagnose you, but I can help you describe what you're going through, "
                "ask clarifying questions, and help you prepare for a visit with a doctor.\n\n"
                "To start, can you tell me what’s bothering you most right now?"
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
        model="gpt-4.1-mini",  # Change model here if you like
        messages=api_messages,
        temperature=0.4,
    )

    return completion.choices[0].message.content.strip()

# ---------- Display chat history ----------

for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "user" else "assistant"):
        st.markdown(message["content"])

# ---------- Input box ----------

user_input = st.chat_input("Tell me what’s going on with your health…")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get model reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking with you..."):
            reply = generate_reply(user_input)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------- Extra: Summarize for your doctor ----------

st.markdown("---")
st.subheader("📝 Create a summary to show your doctor")

st.caption(
    "After a few messages, click the button below. The bot will create a short, structured "
    "summary of your conversation that you can copy into a note or email for your clinician."
)

if st.button("Generate summary for my doctor"):
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
