import streamlit as st
from openai import OpenAI
import re

# Initialize OpenAI client
client = OpenAI()

st.set_page_config(page_title="Hiring Assistant", layout="centered")
st.title(" TalentScout's Hiring Assistant")

# ---------------- Session State ---------------- #

if "step" not in st.session_state:
    st.session_state.step = 0

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a hiring assistant chatbot. "
                "Your task is to collect candidate information and generate "
                "technical interview questions strictly based on the declared tech stack. "
                "Do not provide answers. Do not deviate from hiring purpose."
            )
        }
    ]

# ---------------- Helper Functions ---------------- #

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def generate_questions(tech_stack):
    prompt = f"""
    Generate 3 to 5 technical interview questions for each of the following technologies:
    {tech_stack}

    Rules:
    - No answers
    - Beginner to intermediate level
    - Bullet point format
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a technical interviewer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# ---------------- Display Chat ---------------- #

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Chat Input ---------------- #

user_input = st.chat_input("Type your response...")

if user_input:

    # Exit keywords
    if user_input.lower() in ["exit", "quit", "bye", "end"]:
        add_message("assistant", "Thank you for your time! Our team will contact you soon. 👋")
        st.stop()

    with st.chat_message("user"):
        st.markdown(user_input)

    # Step-based logic
    if st.session_state.step == 0:
        reply = (
            "Hello! 👋 I’m TalentScout, an AI Hiring Assistant.\n\n"
            "I’ll collect some details and ask technical questions based on your skills.\n\n"
            "**What is your full name?**"
        )
        st.session_state.step += 1

    elif st.session_state.step == 1:
        st.session_state.candidate["name"] = user_input
        reply = "Please provide your **email address**."
        st.session_state.step += 1

    elif st.session_state.step == 2:
        if not valid_email(user_input):
            reply = "That doesn’t look like a valid email. Please try again."
        else:
            st.session_state.candidate["email"] = user_input
            reply = "What is your **phone number**?"
            st.session_state.step += 1

    elif st.session_state.step == 3:
        st.session_state.candidate["phone"] = user_input
        reply = "How many **years of experience** do you have?"
        st.session_state.step += 1

    elif st.session_state.step == 4:
        st.session_state.candidate["experience"] = user_input
        reply = "What **position(s)** are you applying for?"
        st.session_state.step += 1

    elif st.session_state.step == 5:
        st.session_state.candidate["position"] = user_input
        reply = "What is your **current location**?"
        st.session_state.step += 1

    elif st.session_state.step == 6:
        st.session_state.candidate["location"] = user_input
        reply = (
            "Please list your **tech stack**.\n"
            "Example: Python, Django, SQL, Power BI"
        )
        st.session_state.step += 1

    elif st.session_state.step == 7:
        st.session_state.candidate["tech_stack"] = user_input
        reply = "Generating technical questions based on your tech stack... ⏳"
        st.session_state.step += 1

        add_message("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)

        questions = generate_questions(user_input)

        final_reply = f"""
### 🔍 Technical Interview Questions

{questions}

Thank you for completing the screening!  
Our recruitment team will review your responses and contact you soon.
"""

        add_message("assistant", final_reply)
        with st.chat_message("assistant"):
            st.markdown(final_reply)
        st.stop()

    else:
        reply = "Thank you for your time!"

    add_message("assistant", reply)
    with st.chat_message("assistant"):
        st.markdown(reply)
