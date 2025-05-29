import spacy
from fuzzywuzzy import fuzz

nlp = spacy.load("en_core_web_md")

# Example equivalence dictionary (should match skill_extractor.py)
SKILL_EQUIVALENCE = {
    "mysql": "sql",
    "oracle": "sql",
    "postgresql": "sql",
    # add more here...
}

def normalize_skill(skill):
    return SKILL_EQUIVALENCE.get(skill.lower(), skill.lower())

def compute_skill_score(resume_skills, job_skills):
    score = 0
    matched_skills = []

    for job_skill in job_skills:
        job_skill_clean = normalize_skill(job_skill)
        job_doc = nlp(job_skill_clean)

        best_match_score = 0
        best_match_skill = None

        for resume_skill in resume_skills:
            resume_skill_clean = normalize_skill(resume_skill)
            resume_doc = nlp(resume_skill_clean)

            try:
                semantic_score = job_doc.similarity(resume_doc)
            except:
                semantic_score = 0.0

            fuzzy_score = fuzz.partial_ratio(job_skill_clean, resume_skill_clean) / 100
            combined_score = (semantic_score + fuzzy_score) / 2

            if combined_score > best_match_score:
                best_match_score = combined_score
                best_match_skill = resume_skill_clean

        if best_match_score >= 0.7:
            score += 1
            matched_skills.append((job_skill_clean, best_match_skill, round(best_match_score, 2)))

    return score, matched_skills
