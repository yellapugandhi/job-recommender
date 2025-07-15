import streamlit as st
import requests
import os

# Set your GROQ API key (store securely in production)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# Available models
MODEL_OPTIONS = {
    "LLaMA 3 (8B)": "llama3-8b-8192",
    "Mixtral (8x7B)": "mixtral-8x7b-32768"
}

st.set_page_config(page_title="Objection Handler with GROQ", layout="wide")
st.title("🎯 Smart Objection Handler - Powered by GROQ LLM")

# Sidebar settings
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.selectbox("Select Model", list(MODEL_OPTIONS.keys()))
temp = st.sidebar.slider(
    "Temperature (Creativity)", 
    0.0, 1.0, 0.7, 0.1, 
    help="""Controls response randomness.

- 0.0 to 0.3: More factual, consistent replies
- 0.4 to 0.6: Balanced and persuasive
- 0.7 to 1.0: Creative, bold, and varied"""
)
tone = st.sidebar.selectbox("Response Tone", ["Confident", "Consultative", "Friendly", "Aggressive"])

# Instruction
st.markdown("Type any message or objection from your prospect. Let AI generate a smart response.")

# User Input for Objection Handling
user_input = st.text_area("🙋 Prospect's Message", placeholder="e.g., Is this an MLM?", height=150)

if st.button("🤖 Generate Response") and user_input:
    with st.spinner("Thinking..."):
        try:
            model_name = MODEL_OPTIONS[model_choice]

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"You are a network marketing mentor. "
                            f"Help the user craft a confident, persuasive reply to a prospect's objection or concern. "
                            f"Use a {tone.lower()} tone."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                "temperature": temp
            }

            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            reply = result['choices'][0]['message']['content']
            st.success("✅ Response:")
            st.write(reply)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Visual Mapping Journey
st.markdown("---")
st.header("🗺️ Visual Prospecting Journey Generator")

st.markdown("Describe anything about your prospecting situation. The AI will understand and guide you from that point to closure.")
stage_input = st.text_area("🧩 Prospecting Context", placeholder="e.g., They showed interest but are now ghosting me.")

if st.button("🔄 Generate Journey") and stage_input:
    with st.spinner("Creating journey map..."):
        try:
            model_name = MODEL_OPTIONS[model_choice]

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a top-tier network marketing strategist. Based on the user's description of their situation with a prospect, generate a custom prospecting roadmap. "
                            "The roadmap should flow logically from the current stage all the way to signup, using psychological insights, communication strategy, and confidence-building steps. "
                            "Avoid hardcoded stage names — adapt fluidly to the user's input."
                        )
                    },
                    {
                        "role": "user",
                        "content": stage_input
                    }
                ],
                "temperature": temp
            }

            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            reply = result['choices'][0]['message']['content']
            st.success("📍 Personalized Prospecting Journey:")
            st.markdown(reply)

        except Exception as e:
            st.error(f"❌ Error generating journey: {str(e)}")
