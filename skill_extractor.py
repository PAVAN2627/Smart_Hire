import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def load_skill_keywords(csv_path="skills.csv"):
    df = pd.read_csv(csv_path)
    return [skill.strip().lower() for skill in df['skill'].dropna().unique()]

# Load raw skill keywords
SKILL_KEYWORDS = load_skill_keywords()

# Define equivalence mapping for normalization
SKILL_EQUIVALENCE = {
    "mysql": "sql",
    "oracle": "sql",
    "postgresql": "sql",
    "postgres": "sql",
    "mariadb": "sql",
    "pl/sql": "sql",
    "tsql": "sql",
    # add more synonyms here as needed
}

def normalize_skill(skill):
    # Map skill to canonical form, if present in equivalence dict
    return SKILL_EQUIVALENCE.get(skill, skill)

def extract_skills(text):
    text_lower = text.lower()
    doc = nlp(text_lower)
    skills_found = set()

    # Match single tokens
    for token in doc:
        if token.text in SKILL_KEYWORDS:
            normalized = normalize_skill(token.text)
            skills_found.add(normalized)

    # Match phrases (multi-word skills)
    for phrase in SKILL_KEYWORDS:
        if phrase in text_lower:
            normalized = normalize_skill(phrase)
            skills_found.add(normalized)

    return list(skills_found)
