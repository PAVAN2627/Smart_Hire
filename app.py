import os
import pandas as pd
import shutil
import io
import json
import streamlit as st
from scorer import compute_skill_score
from text_extractor import extract_text_from_pdf
from skill_extractor import extract_skills
import re
from rapidfuzz import fuzz
from streamlit_tags import st_tags
SKILL_EQUIVALENCE = {
    # SQL databases
    "mysql": "sql",
    "oracle": "sql",
    "postgresql": "sql",
    "mariadb": "sql",
    "sql server": "sql",
    "sqlite": "sql",
    "sql": "sql",

    # NoSQL databases
    "mongodb": "nosql",
    "cassandra": "nosql",
    "dynamodb": "nosql",
    "couchdb": "nosql",
    "redis": "nosql",
    "elasticsearch": "nosql",

    # Programming languages
    "python": "python",
    "java": "java",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "javascript",
    "nodejs": "javascript",
    "c": "c/c++",
    "c++": "c/c++",
    "golang": "go",
    "go": "go",
    "ruby": "ruby",
    "kotlin": "kotlin",
    "swift": "swift",
    "php": "php",

    # Web development
    "html": "frontend",
    "css": "frontend",
    "scss": "frontend",
    "bootstrap": "frontend",
    "tailwind": "frontend",
    "react": "frontend",
    "react.js": "frontend",
    "vue": "frontend",
    "vue.js": "frontend",
    "angular": "frontend",

    # Backend frameworks
    "django": "backend",
    "flask": "backend",
    "express": "backend",
    "spring": "backend",
    "laravel": "backend",
    "fastapi": "backend",

    # Cloud platforms
    "aws": "cloud",
    "azure": "cloud",
    "gcp": "cloud",
    "google cloud": "cloud",
    "google cloud platform": "cloud",
    "heroku": "cloud",
    "vercel": "cloud",
    "netlify": "cloud",

    # DevOps / CI/CD
    "docker": "devops",
    "kubernetes": "devops",
    "jenkins": "devops",
    "github actions": "devops",
    "ansible": "devops",
    "terraform": "devops",

    # Data & ML
    "pandas": "data",
    "numpy": "data",
    "matplotlib": "data",
    "seaborn": "data",
    "scikit-learn": "ml",
    "sklearn": "ml",
    "tensorflow": "ml",
    "keras": "ml",
    "pytorch": "ml",
    "openai": "ml",
    "llm": "ml",

    # Tools
    "git": "tools",
    "github": "tools",
    "bitbucket": "tools",
    "jira": "tools",
    "postman": "tools",
    "figma": "tools",
    "notion": "tools",
}


def normalize_skill(skill):
    skill = skill.lower().strip()
    return SKILL_EQUIVALENCE.get(skill, skill)

def match_skills(jd_skills, resume_skills):
    jd_norm = set(normalize_skill(s) for s in jd_skills)
    resume_norm = set(normalize_skill(s) for s in resume_skills)

    matched = jd_norm & resume_norm

    remaining_jd = jd_norm - matched

    for jd_skill in remaining_jd:
        for res_skill in resume_norm:
            if fuzz.token_sort_ratio(jd_skill, res_skill) >= 80:
                matched.add(jd_skill)
                break

    return matched

if "original_results" not in st.session_state:
    st.session_state.original_results = []

st.title("🤖 AI-Powered Resume Screening Assistant (HR Portal)")

resume_dir = "resumes"
roles = os.listdir(resume_dir)
selected_role = st.selectbox("📂 Select Job Role to Review", roles)

folder_path = os.path.join(resume_dir, selected_role)
resume_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

# ✅ Auto-load JD from file silently
jd_path = os.path.join(folder_path, "job_description.txt")
job_description = ""
if os.path.exists(jd_path):
    with open(jd_path, "r", encoding="utf-8") as f:
        job_description = f.read()

# Display JD extracted skills
jd_skills = extract_skills(job_description)
st.subheader("📌 Key Skills from Job Description (JD)")
if jd_skills:
    st.markdown(f"`{', '.join(jd_skills)}`")
else:
    st.markdown("_No skills found in JD._")

# Filters
experience_years = st.multiselect("📅 Required Work Experience (in years)", [1, 2, 3, 4, 5, 6])

programming_languages = st.multiselect("💻 Required Programming Languages", [
    "", "python", "php", "java", "c++", "javascript", "sql", "react", "node.js", "django", "flask", "git"
])

eligibility_keywords = st.multiselect(
    "📜 Eligibility Criteria (e.g., B.Tech, M.Sc, Diploma)",
    ["B.Tech", "BE", "M.Tech", "ME", "B.Sc", "M.Sc", "MBA", "Diploma", "10th", "12th"]
)

apply_filters_button = st.button("🔍 Apply Filters")
clear_filters_button = st.button("❌ Clear Filters")

# Analyze Resumes
if job_description and st.button("📊 Analyze Resumes"):
    results = []

    for file in resume_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'rb') as f:
            text = extract_text_from_pdf(f)

        score = compute_skill_score(text, job_description)
        if isinstance(score, tuple):
            score = score[0]
        score = min(max(int(score), 0), 100)  # Ensure within 0–100

        resume_skills = extract_skills(text)

        matched_skills = match_skills(jd_skills, resume_skills)
        missing_skills = set(jd_skills) - matched_skills

        match_score = len(matched_skills) / len(jd_skills) * 100 if jd_skills else 0
        job_fit = (
            "✅ Best Fit" if match_score >= 80 else
            "🟡 Average Fit" if match_score >= 50 else
            "🔴 Low Fit"
        )

        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        email = email_match.group(0) if email_match else "Not Found"

        results.append({
            "name": file,
            "email": email,
            "score": score,
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "job_fit": job_fit,
            "resume_skills": resume_skills,
            "text": text.lower()
        })

    st.session_state.original_results = results
    st.session_state.filtered_results = results

# Filter Logic
if apply_filters_button:
    filtered = []
    for result in st.session_state.original_results:
        resume_skills_lower = [skill.lower() for skill in result["resume_skills"]]
        resume_text = result["text"]

        # ✅ Experience Filter
        if experience_years:
            if not any(f"{yr} year" in resume_text or f"{yr} years" in resume_text for yr in experience_years):
                continue

        # ✅ Eligibility Filter - ALL selected must be present
        if eligibility_keywords:
            if not all(kw.lower() in resume_text for kw in eligibility_keywords):
                continue

        # ✅ Programming Language Filter
        passes_language_filter = True
        extra_matched = set()
        if programming_languages:
            for lang in programming_languages:
                if any(fuzz.token_sort_ratio(lang.lower(), skill.lower()) >= 80 for skill in resume_skills_lower):
                    extra_matched.add(lang.lower())
                else:
                    passes_language_filter = False
                    break

        if programming_languages and not passes_language_filter:
            continue

        result["matched_skills"].update(extra_matched)

        updated_match_score = len(result["matched_skills"].intersection(jd_skills)) / len(jd_skills) * 100 if jd_skills else 0
        result["match_score"] = updated_match_score

        result["job_fit"] = (
            "✅ Best Fit" if updated_match_score >= 80 else
            "🟡 Average Fit" if updated_match_score >= 50 else
            "🔴 Low Fit"
        )

        filtered.append(result)

    st.session_state.filtered_results = filtered

    if not filtered:
        st.warning("❗ No resumes matched the filters. Try adjusting skill or experience criteria.")

if clear_filters_button and "original_results" in st.session_state:
    st.session_state.filtered_results = st.session_state.original_results

# Show Results
if "filtered_results" in st.session_state:
    st.subheader("✅ Resume Match Results")
    for res in sorted(st.session_state.filtered_results, key=lambda x: x["score"], reverse=True):
        st.markdown(f"📄 **{res['name']}** — Match Score: **{round(res['match_score'], 2)}%**")
        st.markdown(f"📧 Email: `{res['email']}`")
        st.markdown(f"🌟 Fit Level: **{res['job_fit']}**")

        # Highlight JD skills
        highlighted_skills = []
        for skill in jd_skills:
            if skill in res['matched_skills']:
                highlighted_skills.append(f"✅ **{skill}**")
            else:
                highlighted_skills.append(f"❌ *{skill}*")

        st.markdown("🎯 **JD Skill Match:**<br>" + ", ".join(highlighted_skills), unsafe_allow_html=True)

        st.markdown(f"🎯 Matched Skills: `{', '.join(res['matched_skills'])}`")
        st.markdown(f"❌ Missing Skills: `{', '.join(res['missing_skills'])}`")
        st.progress(res['score'])
        st.markdown("---")

    # CSV Download
    if st.session_state.filtered_results:
        sorted_results = sorted(st.session_state.filtered_results, key=lambda x: x["score"], reverse=True)

        csv_data = []
        for idx, res in enumerate(sorted_results, start=1):
            csv_data.append({
                "Rank": idx,
                "Name": res['name'],
                "Match Score (%)": round(res['match_score'], 2),
                "Fit Level": res['job_fit'],
                "Matched Skills": ", ".join(res['matched_skills']),
                "Missing Skills": ", ".join(res['missing_skills']),
                "Resume Score": res['score']
            })

        df = pd.DataFrame(csv_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Download Ranked Filtered Results as CSV",
            data=csv_buffer.getvalue(),
            file_name="ranked_filtered_resumes.csv",
            mime="text/csv"
        )

# Post New Job Role Section
st.header("📝 Post a New Job Role")

with st.form("job_post_form"):
    new_role = st.text_input("Job Role Title")
    new_desc = st.text_area("Skills Required")
    new_location = st.text_input("Job Location")
    new_eligibility = st.text_area("Eligibility Criteria")

    submit_post = st.form_submit_button("🚀 Post Job")

    if submit_post:
        if not new_role or not new_desc or not new_location or not new_eligibility:
            st.warning("⚠️ Please fill in all job details.")
        else:
            job_entry = {
                "description": new_desc,
                "location": new_location,
                "eligibility": new_eligibility
            }

            jobs_file = "jobs.json"
            if os.path.exists(jobs_file):
                with open(jobs_file, "r") as f:
                    jobs_data = json.load(f)
            else:
                jobs_data = {}

            jobs_data[new_role] = job_entry

            with open(jobs_file, "w") as f:
                json.dump(jobs_data, f, indent=4)

            # ✅ Create folder and save JD
            new_role_folder = os.path.join("resumes", new_role)
            os.makedirs(new_role_folder, exist_ok=True)
            jd_path = os.path.join(new_role_folder, "job_description.txt")
            with open(jd_path, "w", encoding="utf-8") as jd_file:
                jd_file.write(new_desc)

            st.success(f"✅ Job '{new_role}' posted successfully and directory created!")
            st.header("🗑️ Delete Posted Job Roles")

jobs_file = "jobs.json"
if os.path.exists(jobs_file):
    with open(jobs_file, "r") as f:
        jobs_data = json.load(f)
else:
    jobs_data = {}

if jobs_data:
    # Show multiselect of posted jobs to delete
    jobs_to_delete = st.multiselect("Select Job Roles to Delete", list(jobs_data.keys()))

    if st.button("🗑️ Delete Selected Job Roles"):
        if not jobs_to_delete:
            st.warning("⚠️ Please select at least one job role to delete.")
        else:
            for job in jobs_to_delete:
                # Remove job from jobs.json
                if job in jobs_data:
                    del jobs_data[job]

                # Delete job folder and its contents
                job_folder = os.path.join("resumes", job)
                if os.path.exists(job_folder):
                    try:
                        shutil.rmtree(job_folder)
                    except Exception as e:
                        st.error(f"Failed to delete folder for job '{job}': {e}")

            # Update jobs.json
            with open(jobs_file, "w") as f:
                json.dump(jobs_data, f, indent=4)

            st.success(f"✅ Deleted selected job roles and their resume folders successfully!")
else:
    st.info("No job roles posted yet.")
