import streamlit as st
import requests
import os
import base64
from fpdf import FPDF
import re

# === CONFIG ===
st.set_page_config(page_title="Career Planner", layout="centered")
st.title("💼 Career Planner & Role Recommender")
st.markdown("Powered by LLaMA-3 (via Groq)")

# === Groq API ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")  # Replace or export

def call_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else f"❌ LLM Error ({response.status_code}): {response.text}"

# === UTILS ===
def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    safe_content = remove_emojis(content)
    for line in safe_content.split("\n"):
        pdf.multi_cell(0, 10, line)
    return pdf

# === INPUT FORM ===
skills = st.text_input("🧠 Your current skills (comma-separated)")
interest = st.text_input("🎯 What’s your primary interest or industry?")
education = st.selectbox("🎓 Education level", ["High School", "Bachelor's Degree", "Master's Degree", "PhD", "Other"])
experience_years = st.slider("🕒 Years of experience", 0, 30, 2)
learning_level = st.slider("📚 Willingness to learn (1–10)", 1, 10, 7)
resume_file = st.file_uploader("📄 Upload your resume (optional)", type=["txt", "pdf"])

submit = st.button("🚀 Get My Career Plan")
recommendation_sections = []

# === RESUME REVIEW ===
if resume_file:
    st.subheader("🔍 Resume Feedback")
    resume_text = resume_file.read().decode("utf-8", errors="ignore")
    review_prompt = f"Review this resume and give suggestions:\n\n{resume_text}\n\nBe brief, mention strengths and improvement points."
    review_output = call_llm(review_prompt)
    st.markdown(review_output)
    recommendation_sections.append("### Resume Review\n" + review_output)

# === MAIN FLOW ===
if submit:
    user_data = {
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
        "interest": interest,
        "education": education,
        "experience_years": experience_years,
        "learning_level": learning_level
    }

    with st.spinner("🤖 Thinking..."):

        # 1. Role Recommendations
        prompt_roles = f"""
        User profile:
        - Skills: {', '.join(user_data['skills'])}
        - Interest: {interest}
        - Education: {education}
        - Experience: {experience_years} years
        - Learning Willingness: {learning_level}/10

        Suggest 2 best career roles for them with short reasons. Format:
        1. Role - Reason
        2. Role - Reason
        """
        roles_output = call_llm(prompt_roles)
        st.subheader("🎯 Recommended Roles")
        st.markdown(roles_output)
        recommendation_sections.append("### Recommended Roles\n" + roles_output)

        # Extract roles
        roles = []
        for line in roles_output.split("\n"):
            if line.strip().startswith(("1.", "2.")) and "-" in line:
                role = line.split("-")[0].replace("1.", "").replace("2.", "").strip()
                roles.append(role)

        # 2. Roadmaps with Course Suggestions
        for role in roles:
            roadmap_prompt = f"""
            Provide a 3-phase learning roadmap to become a {role}. Include 3–5 items per phase and link free online courses (YouTube, Coursera, etc.).
            Format:
            ### {role} Roadmap
            **Beginner**:
            - Topic - Course/Link
            ...
            """
            roadmap = call_llm(roadmap_prompt)
            st.subheader(f"📘 {role} Learning Roadmap + Courses")
            st.markdown(roadmap)
            recommendation_sections.append(f"### {role} Roadmap\n" + roadmap)

        # 3. Salary Projection
        for role in roles:
            salary_prompt = f"""
            Estimate salary growth in India for a {role} with:
            - {experience_years} years experience
            - Education: {education}
            - Learning willingness: {learning_level}/10

            Provide:
            - Starting salary (₹)
            - Annual growth rate (%)
            - 10-year salary projection

            Format:
            **Starting Salary**: ₹X  
            **Growth Rate**: Y%  
            **10-Year Projection**:
            Year 1: ₹X1  
            Year 2: ₹X2  
            ...
            """
            salary = call_llm(salary_prompt)
            st.subheader(f"📈 {role} Salary Projection")
            st.markdown(salary)
            recommendation_sections.append(f"### {role} Salary Projection\n" + salary)

        # 4. Mock Interview Questions
        for role in roles:
            interview_prompt = f"""
            Give 5 mock interview questions (with answers) for a {role}.
            Include both technical and behavioral questions.
            """
            interview = call_llm(interview_prompt)
            st.subheader(f"🧾 {role} Mock Interview Q&A")
            st.markdown(interview)
            recommendation_sections.append(f"### {role} Mock Interview Q&A\n" + interview)

        # 5. PDF Export
        combined_text = "\n\n".join(recommendation_sections)
        pdf = create_pdf(combined_text)
        pdf_path = "/tmp/career_plan.pdf"
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Career Plan as PDF",
                data=f,
                file_name="career_plan.pdf",
                mime="application/pdf"
            )
