# 🚀 Smart Hire - AI-Powered Resume Screening Assistant

![Python](https://img.shields.io/badge/python-3.10-blue)
![NLP](https://img.shields.io/badge/NLP-spaCy-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-active-success)

Smart Hire is an AI-powered system that automates resume screening and job matching using Natural Language Processing (NLP). It consists of a two-sided platform:

- ✅ **HR Portal** (Streamlit): Post jobs, upload resumes, and get skill match scores.
- 👤 **Jobseeker Portal** (Flask): View and apply for available jobs by uploading a resume.

---

## 📸 Screenshots

### 🔹 HR Portal (Streamlit)

![output1](https://github.com/user-attachments/assets/675d7926-41ef-4488-ac56-d5c476fedc9e)


![output2](https://github.com/user-attachments/assets/b3204a14-316a-4b57-b0c4-894dba010c91)


---

### 🔹 Jobseeker Portal (Flask)



![op3](https://github.com/user-attachments/assets/149bca56-28b3-4365-86ce-e06b45ba86a9)


## 🧠 Features

### 🏢 HR Side
- Post job roles with eligibility and descriptions
- Upload resumes to screen
- Skill extraction using spaCy
- Semantic & fuzzy skill match scoring (TF-IDF + spaCy + FuzzyWuzzy)
- Delete job roles and auto-delete associated resumes

### 🧑‍💼 Jobseeker Side
- Browse job roles from `jobs.json`
- Upload resume for selected role
- Resumes saved in role-specific folders

---

## 🛠️ Technologies Used

| Component         | Technology              |
|------------------|-------------------------|
| Frontend (HR)    | Streamlit               |
| Frontend (Jobseeker) | HTML, Bootstrap      |
| Backend          | Flask                   |
| NLP & Scoring    | spaCy, FuzzyWuzzy, TF-IDF |
| PDF Extraction   | PyMuPDF (`fitz`)        |
| Data Storage     | Filesystem (`resumes/`, `jobs.json`) |

---


## Set up Virtual Environment

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

## Install Dependencies

pip install -r requirements.txt
python -m spacy download en_core_web_md

## Run the Applications
✅ Start Flask App (Jobseeker)

python flask_backend.py

Visit: http://localhost:5000

## Start Streamlit App (HR)

python -m streamlit run app.py

Visit: Streamlit automatically opens in your browser.

### How It Works

HR posts job → Description saved under a new folder.

Jobseeker applies → Resume stored in the same folder.

HR uploads resumes → System extracts skills.

Matching → Resume skills are scored against job description.

Result → Skill match score with matching breakdown.

Delete → HR can delete job and related data.
