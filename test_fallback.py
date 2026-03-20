import streamlit as st
import requests
from PyPDF2 import PdfReader
from extraction.agents import ProfileExtractor
from gap_identification.agents import GapIdentifierAgent
import traceback
from planning.agents import RoadMapAgent,MockInterviewAgent

from dotenv import load_dotenv
import os

load_dotenv()
openai_key = 'idk'

st.set_page_config(page_title="Skill Bridge Navigator", layout="wide")

ROLES = [
    "Machine Learning Engineer",
    "Data Scientist",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Cloud Engineer",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "Data Analyst",
    "AI Researcher"
]


def extract_text_from_pdf(file):
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t
    return text


def extract_github_text(url):
    try:
        parts = url.rstrip("/").split("/")
        user, repo = parts[-2], parts[-1]

        url_main = f"https://raw.githubusercontent.com/{user}/{repo}/main/README.md"
        url_master = f"https://raw.githubusercontent.com/{user}/{repo}/master/README.md"

        r = requests.get(url_main)
        if r.status_code != 200:
            r = requests.get(url_master)

        if r.status_code == 200:
            return r.text[:5000]
        return ""
    except:
        return ""


st.title("Skill-Bridge Career Navigator")

c1, c2, c3 = st.columns(3)

with c1:
    pdf_file = st.file_uploader("Resume PDF", type=["pdf"])

with c2:
    text_input = st.text_area("Resume / Skills", height=200)

with c3:
    github_url = st.text_input("GitHub Repo URL")

selected_role = st.selectbox("Target Role", ROLES)

if st.button("Process"):
    combined_text = ""

    if pdf_file:
        combined_text += extract_text_from_pdf(pdf_file)

    if text_input:
        combined_text += "\n" + text_input

    if github_url:
        combined_text += "\n" + extract_github_text(github_url)

    if not combined_text.strip():
        st.error("Provide input")
    else:
        st.session_state["profile_text"] = combined_text
        st.session_state["role"] = selected_role

        try:
            # =========================
            # 🔥 PROFILE EXTRACTION
            # =========================
            p = ProfileExtractor(
                "gpt-4o-mini",
                openai_key,
                selected_role
            )

            profile_json = p.run(combined_text)
            st.session_state["profile_json"] = profile_json

            st.subheader("Extracted Profile")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Skills")
                for skill in profile_json.get("skills", []):
                    st.write(f"- {skill}")

            with col2:
                st.markdown("### Projects")
                for proj in profile_json.get("projects", []):
                    st.write(f"- {proj}")

            st.markdown("### Experience")
            st.write(profile_json.get("experience", ""))

            # =========================
            # ⚡ GAP IDENTIFICATION
            # =========================
            g = GapIdentifierAgent(
                "gpt-4o-mini",
                openai_key,
                selected_role
            )

            gap_result = g.run(profile_json)
            st.session_state["gap_json"] = gap_result

            st.subheader("Skill Gap Analysis")

            col3, col4 = st.columns(2)

            with col3:
                st.markdown("### Core Missing Skills")
                for skill in gap_result.get("core_missing", []):
                    st.write(f"- {skill}")

            with col4:
                st.markdown("### Bonus Skills")
                for skill in gap_result.get("bonus_skills", []):
                    st.write(f"- {skill}")

            r = RoadMapAgent(
                "gpt-4o-mini",
                openai_key,
                selected_role
            )
            roadmap_generated = r.run(gap_result)
            st.session_state["roadmap_generated"] = roadmap_generated
            st.subheader("Roadmap")

            col5, col6, col7 = st.columns(3)

            with col5:
                st.markdown("### Learning Path")
                for skill in roadmap_generated.get("learning_path", []):
                    st.write(f"- {skill}")

            with col6:
                st.markdown("### Projects")
                for skill in roadmap_generated.get("projects", []):
                    st.write(f"- {skill}")
            with col7:
                st.markdown("### Resources")
                for skill in roadmap_generated.get("resources", []):
                    st.write(f"- {skill}")

            i = MockInterviewAgent(
                "gpt-4o-mini",
                openai_key,
                selected_role
            )
            interview = i.run(profile_json.get("skills", []))
            st.session_state["interview"] = interview
            st.subheader("Mock Interview (Based on Skills in Resume)")

            #col8 = st.columns(1)

            #with col8:
            st.markdown("### Questions")
            for skill in interview.get("questions", []):
                st.write(f"- {skill}")

        except Exception as e:
            st.error("Pipeline failed")
            st.code(traceback.format_exc())