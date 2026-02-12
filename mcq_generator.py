import streamlit as st
import json
from dotenv import load_dotenv
import os
from openai import OpenAI

# -----------------------------
# ENV SETUP
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# SUBJECT → TOPIC MAPPING
# -----------------------------
SUBJECT_TOPICS = {
    "Computer Science": [
        "Operating Systems", "Data Structures", "Computer Networks",
        "Databases", "Software Engineering"
    ],
    "Mathematics": [
        "Arithmatic","Algebra", "Calculus", "Probability", "Statistics", "Linear Algebra","Geometry"
    ],
    "Statistics": [
        "Probability Theory","Mathematical Statistics", "Applied Statistics", "Computational Statistics", "Bayesian Statistics", "Non-parametric Statistics","Multivariate Statistics","Time Series Analysis","Statistical Learning (Modern)"
    ],
    "Physics": [
        "Mechanics", "Thermodynamics", "Optics",
        "Electromagnetism", "Modern Physics"
    ],
    "Chemistry": [
        "Organic Chemistry", "Inorganic Chemistry",
        "Physical Chemistry", "Biochemistry"
    ],
    "Biology": [
        "Cell Biology", "Genetics", "Human Physiology",
        "Ecology", "Evolution"
    ],
    "History": [
        "Ancient History", "Medieval History",
        "Modern History", "World History"
    ],
    "Geography": [
        "Physical Geography", "Human Geography",
        "Climatology", "Environmental Geography"
    ],
    "AI & ML": [
        "Machine Learning", "Deep Learning",
        "NLP", "Computer Vision", "Reinforcement Learning"
    ],
    "Data Science": [
        "Data Analysis", "Data Visualization",
        "Statistics", "Big Data", "Data Engineering"
    ]
}

# -----------------------------
# HELPERS
# -----------------------------
def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "")
    return text.rstrip(", \n")

# -----------------------------
# LLM CALL
# -----------------------------
def generate_mcqs(subject, topic, difficulty, num_questions):
    prompt = f"""
You are an expert question paper setter.

Generate {num_questions} multiple-choice questions for:
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Rules:
- Each question must have 4 options
- Only one correct answer
- Return ONLY valid JSON (no markdown)

JSON format:
[
  {{
    "question": "",
    "options": ["", "", "", ""],
    "answer": ""
  }}
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate exam-quality MCQs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="MCQ Quiz Generator", layout="wide")
st.title("📘 MCQ Quiz Generator (Subject → Topic)")
st.write("LLM-powered quiz with scoring")

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("⚙️ Quiz Settings")

    subject = st.selectbox("Select Subject", list(SUBJECT_TOPICS.keys()))
    topic = st.selectbox("Select Topic", SUBJECT_TOPICS[subject])

    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    num_questions = st.slider("Number of Questions", 1, 50, 5)

    generate_btn = st.button("🚀 Generate Quiz")

# -----------------------------
# GENERATE QUIZ
# -----------------------------
if generate_btn:
    with st.spinner("Generating quiz questions..."):
        result = generate_mcqs(subject, topic, difficulty, num_questions)
        mcqs = json.loads(clean_json(result))

        st.session_state.mcqs = mcqs
        st.session_state.answers = {}
        st.session_state.submitted = False

        st.success("Quiz Ready! Start answering 👇")

# -----------------------------
# RENDER QUIZ
# -----------------------------
if "mcqs" in st.session_state and not st.session_state.submitted:

    for idx, mcq in enumerate(st.session_state.mcqs, start=1):
        st.markdown(f"### Q{idx}. {mcq['question']}")

        selected = st.radio(
            label="",
            options=mcq["options"],
            index=None,
            key=f"q_{idx}"
        )

        st.session_state.answers[idx] = selected
        st.divider()

    if st.button("🧮 Submit Quiz"):
        st.session_state.submitted = True

# -----------------------------
# RESULTS
# -----------------------------
if st.session_state.get("submitted", False):

    score = 0
    for idx, mcq in enumerate(st.session_state.mcqs, start=1):
        if st.session_state.answers.get(idx) == mcq["answer"]:
            score += 1

    st.subheader("📊 Quiz Result")
    st.success(f"Your Score: **{score} / {len(st.session_state.mcqs)}**")

    with st.expander("📘 View Correct Answers"):
        for idx, mcq in enumerate(st.session_state.mcqs, start=1):
            st.markdown(
                f"**Q{idx}. {mcq['question']}**  \n✅ Correct Answer: `{mcq['answer']}`"
            )
