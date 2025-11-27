# Health_chatbuddy
A **Streamlit-based chatbot** that helps you **reflect on your health, organize symptoms, and prepare a summary for a doctor**.
# 🩺 Health Reflection Chatbot (Streamlit + OpenAI)

A **Streamlit-based chatbot** that helps you **reflect on your health, organize symptoms, and prepare a summary for a doctor**.

> ⚠️ **Important:**  
> This app is **not** a doctor or therapist.  
> It does **not** diagnose, detect conditions, or provide medical advice.  
> Always consult a qualified health professional for medical concerns or emergencies.

---

## 🚀 Features

- 💬 Chat-style interface using **Streamlit’s `st.chat_message` + OpenAI Chat Completions**
- 🧠 System prompt designed to:
  - Ask gentle, clarifying questions
  - Help you describe symptoms in a structured way
  - Prepare a **summary to share with your doctor**
- 🛡️ Safety guardrails:
  - Repeatedly reminds you it’s **not** a clinician
  - Avoids diagnosis / “detecting what’s wrong”
  - Encourages seeking professional help, especially for severe/urgent issues

---

## 🧩 Tech Stack

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://platform.openai.com/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📦 Installation

### 1️⃣ Clone the repo

```bash
git clone https://github.com/<your-username>/health-reflection-chatbot.git
cd health-reflection-chatbot
