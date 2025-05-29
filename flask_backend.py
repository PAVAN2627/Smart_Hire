import os
import json
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Dynamically load job roles and descriptions every time
def load_jobs():
    with open('jobs.json', 'r') as f:
        return json.load(f)

@app.route('/')
def home():
    with open('jobs.json', 'r') as f:
        jobs = json.load(f)
    return render_template('apply.html', jobs=jobs)



@app.route('/apply', methods=['POST'])
def apply():
    name = request.form.get('name', 'anonymous')
    job_roles = request.form.getlist('job_roles')
    file = request.files['resume']

    if not file or not job_roles:
        return "Please select at least one job role and upload a resume.", 400

    filename = secure_filename(f"{name}_{file.filename}")
    file.seek(0)

    jobs = load_jobs()

    for role in job_roles:
        folder = os.path.join(app.config['UPLOAD_FOLDER'], role.lower().replace(" ", "_"))
        os.makedirs(folder, exist_ok=True)

        file.seek(0)
        file.save(os.path.join(folder, filename))

        # ✅ Save JD in a file (only once per role)
        jd_path = os.path.join(folder, "job_description.txt")
        if not os.path.exists(jd_path):
            with open(jd_path, "w") as jd_file:
                jd_file.write(jobs[role]["description"])

    return f"✅ Resume submitted for: {', '.join(job_roles)}"

if __name__ == '__main__':
    app.run(debug=True)
