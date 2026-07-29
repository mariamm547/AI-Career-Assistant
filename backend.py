"""
backend.py
==========
AI Career Assistant — backend logic.

This module is a refactor of the original research/notebook script
(project.py). All of the original logic is preserved:

  - PDF text extraction (PyPDF2)
  - Resume field/skill extraction using Mistral-Nemo-Instruct-2407 via
    a LangChain StructuredOutputParser
  - Loading + cleaning the four Kaggle datasets (company, job-titles,
    data-jobs, resume-jobs)
  - The frequency-filtered job matching engine (a skill only counts as
    "required" for a job title once it clears MIN_SKILL_FREQUENCY across
    at least MIN_POSTINGS postings) — this replaced an earlier "union of
    every skill ever mentioned" approach that made common titles balloon
    to hundreds of required skills
  - The Mistral-based career-advice report (build_job_recommendation_prompt
    + generate_text + format_mistral_output)

What changed turning it into a backend module (all behavior-preserving
unless noted):

  1. Everything that used to run at import time (model loading, dataset
     downloads) now happens lazily, the first time it's actually needed,
     and is cached afterward. Running `import backend` no longer takes
     10+ minutes or requires a GPU.
  2. Three public entry points were added to match the required
     interface: extract_skills_from_resume(pdf_file), recommend_jobs(skills),
     recommend_missing_skills(skills).
  3. `dataset_text4`'s column list had a typo ("Job Experience wRequired")
     that would raise a pandas usecols error — the four selected columns
     are now trimmed down to just the three actually used downstream
     (Job Title, Industry, Key Skills), which also makes loading more
     robust to that dataset's exact schema.
  4. The per-job "reason" shown on the Job Recommendation cards is now a
     fast template built from matched skills, so recommend_jobs() stays
     instant for 10 jobs at once. The original Mistral-authored, full
     multi-job written report (strengths / rankings / roadmap) is still
     generated exactly as before — call generate_career_advice() for it.
  5. `faiss`, `FAISS`, `HuggingFaceEmbeddings`, `PyPDFLoader`, and
     `CharacterTextSplitter` were imported in the original script but
     never exercised by the logic shown (per project notes, reserved for
     a future RAG/vector-store layer). They're kept as optional imports
     below so this module still loads without them if that layer isn't
     installed yet.

Heavy third-party imports (torch/transformers/langchain/kagglehub) are
wrapped in a try/except so this file can still be imported (e.g. to read
docstrings, or from a machine without a GPU) without crashing. Calling a
function that actually needs them will raise a clear RuntimeError if
they're missing.
"""

import re
import ast
import json
from collections import defaultdict, Counter

import pandas as pd
import requests
from PyPDF2 import PdfReader
import kagglehub
from langchain_classic.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Dataset loading state (lazy)
# ---------------------------------------------------------------------------
DATASETS_LOADED = False

# Populated by _ensure_datasets_loaded(); module-level so all functions share
# the same in-memory matching structures once loaded.
JOB_TO_SKILLS = {}
JOB_POSTING_COUNTS = defaultdict(int)
JOB_TO_COMPANIES = defaultdict(set)
SKILL_TO_JOBS = defaultdict(set)
JOB_TO_INDUSTRY = {}
COMPANY_TO_SECTOR = {}
INDUSTRY_TO_COMPANIES = defaultdict(set)


# ---------------------------------------------------------------------------
# Mistral API helper (centralised HTTP calls with error handling & timeout)
# ---------------------------------------------------------------------------
MISTRAL_API_URL = "https://pamphlet-sleek-glowworm.ngrok-free.dev/generate"
MISTRAL_API_KEY = "pass123"

def _call_mistral_api(prompt, max_length=4500, timeout=90, retries=3):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    payload = {"prompt": prompt, "max_length": max_length}
    for attempt in range(retries):
        try:
            response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            return data["response"]
        except requests.exceptions.Timeout:
            if attempt == retries - 1:
                raise RuntimeError(f"Mistral API request timed out after {retries} attempts.")
            # wait and retry with longer timeout? We'll just increase timeout each retry.
            timeout += 30
            continue
        except requests.exceptions.RequestException as e:
            # For other errors, we can retry too, but maybe not for non-timeout?
            # We'll retry for any request exception except maybe 4xx/5xx? But we'll retry all.
            if attempt == retries - 1:
                raise RuntimeError(f"Mistral API request failed: {e}")
            # wait a bit before retry
            import time
            time.sleep(2)
            continue
    raise RuntimeError("Mistral API request failed after retries.")

# ---------------------------------------------------------------------------
# PDF text extraction (lightweight, no ML deps)
# ---------------------------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    """Extract raw text from a PDF.

    Accepts either a filesystem path (str) or a file-like object such as
    Streamlit's UploadedFile — PyPDF2's PdfReader supports both directly.
    """
    reader = PdfReader(pdf_file)
    full_text = ""
    for page in reader.pages:
        full_text += (page.extract_text() or "") + "\n"
    return full_text


# ---------------------------------------------------------------------------
# Structured resume-field extraction (name/email/education/skills/experience)
# ---------------------------------------------------------------------------
def _build_output_parser():
    fullName_schema = ResponseSchema(
        name="full_name",
        description="A string containing the candidate's complete name as it appears in the resume.",
    )
    email_schema = ResponseSchema(
        name="email", description="A string containing the candidate's email address."
    )
    education_schema = ResponseSchema(
        name="education",
        description="A list of education records. Each record should contain: degree (string), institution (string), and year (string).",
    )
    skills_schema = ResponseSchema(
        name="skills",
        description="A list of the candidate's technical and professional skills as strings.",
    )
    experience_schema = ResponseSchema(
        name="experience",
        description="A list of work experience records. Each record should contain: role (string), company (string), and years (string).",
    )
    response_schemas = [fullName_schema, email_schema, education_schema, skills_schema, experience_schema]
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return parser, parser.get_format_instructions()


RESUME_EXTRACTION_TEMPLATE = """
You are a smart HR assistant that extracts candidate information from resumes.

Extract:
- full_name
- email
- education (degree, institution, year)
- skills
- experience (role, company, years)

Respond ONLY in JSON format as follows:
{format_instructions}

Now extract the information from the following resume:

{user_input}

"""


def extract_json_block(text):
    """Pull the JSON payload out of a ```json ... ``` fenced block."""
    pattern = r"```json\s*(.*?)\s*```"
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        return text
    return f"```json\n{matches[-1]}\n```"


def _parse_structured_json(json_string):
    """Best-effort parse of the model's JSON block into a plain dict."""
    match = re.search(r"```json\s*(.*?)\s*```", json_string, re.DOTALL)
    if match:
        json_string = match.group(1)
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, AttributeError):
        return {}


def extract_skills(json_string):
    """Extract just the skills list from a JSON string (kept from original)."""
    data = _parse_structured_json(json_string)
    return data.get("skills", []) if isinstance(data, dict) else []


def extract_skills_from_resume(pdf_file):
    """
    Public entry point #1.

    Runs the full resume-parsing pipeline: PDF -> raw text -> Mistral ->
    structured fields. Returns a dict:

        {
            "full_name": str,
            "email": str,
            "education": list,
            "experience": list,
            "skills": list[str],
            "raw_text": str,
        }
    """
    _, format_instructions = _build_output_parser()
    raw_text = extract_text_from_pdf(pdf_file)

    prompt = PromptTemplate(
        template=RESUME_EXTRACTION_TEMPLATE,
        input_variables=["user_input", "format_instructions"],
    ).format(user_input=raw_text, format_instructions=format_instructions)

    answer = _call_mistral_api(prompt, max_length=4500)
    json_text = extract_json_block(answer)
    data = _parse_structured_json(json_text)

    return {
        "full_name": data.get("full_name", ""),
        "email": data.get("email", ""),
        "education": data.get("education", []),
        "experience": data.get("experience", []),
        "skills": data.get("skills", []) or extract_skills(json_text),
        "raw_text": raw_text,
    }


# ---------------------------------------------------------------------------
# Skill / job-title cleaning (unchanged from original)
# ---------------------------------------------------------------------------
SKILL_ALIASES = {
    "py": "python",
    "python programming": "python",
    "js": "javascript",
    "ts": "typescript",
    "c sharp": "c#",
    "c-sharp": "c#",
    "golang": "go",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "ms sql": "sql server",
    "mssql": "sql server",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure cloud": "azure",
    "k8s": "kubernetes",
    "github": "git",
    "gitlab": "git",
    "powerbi": "power bi",
    "excel spreadsheets": "excel",
    "oop": "object oriented programming",
    "rest": "rest api",
    "api": "rest api",
}

JOB_ALIASES = {
    "ml engineer": "machine learning engineer",
    "ml developer": "machine learning engineer",
    "software developer": "software engineer",
    "software programmer": "software engineer",
    "backend engineer": "backend developer",
    "frontend engineer": "frontend developer",
    "data analyst sr": "senior data analyst",
    "sr data analyst": "senior data analyst",
    "sr. data analyst": "senior data analyst",
    "sr data scientist": "senior data scientist",
    "sr. data scientist": "senior data scientist",
    "devops eng": "devops engineer",
}

JOB_TITLE_ALIASES = {
    "ml engineer": "machine learning engineer",
    "sr data scientist": "senior data scientist",
    "sr. data scientist": "senior data scientist",
}


def clean_text(text):
    if pd.isna(text):
        return None
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def clean_company(company):
    company = clean_text(company)
    if company is None:
        return None
    company = company.replace("corporation", "")
    company = company.replace("corp.", "")
    company = company.replace("inc.", "")
    company = company.replace("ltd.", "")
    return company.strip()


def clean_job(job):
    job = clean_text(job)
    if job is None:
        return None
    return JOB_ALIASES.get(job, job)


def clean_sector(sector):
    sector = clean_text(sector)
    if sector is None:
        return None
    return sector.replace("...", "")


def clean_skill(skill):
    skill = clean_text(skill)
    if skill is None:
        return None
    return SKILL_ALIASES.get(skill, skill)


def clean_job_title(raw):
    """One job title string -> canonical lowercase form, or None if empty.

    Postings often tack on location or a specialization after a separator
    ("Machine Learning Engineer || Gurgaon/Chandigarh", "Data Scientist -
    SQL/NoSQL"). Keeping only the text before the first such separator lets
    those merge into one canonical bucket instead of each becoming its own
    barely-populated, unreliable job entry.
    """
    if pd.isna(raw):
        return None
    s = str(raw).strip()
    s = re.split(r"\|\||\||\s-\s|\(|:", s)[0]
    s = re.sub(r"\s+", " ", s).strip().lower()
    if not s:
        return None
    return JOB_TITLE_ALIASES.get(s, s)


def parse_skills(skill_text):
    """'Python, SQL' / 'Python|SQL' / "['Python','SQL']" -> ['python','sql']."""
    if pd.isna(skill_text):
        return []
    skill_text = str(skill_text).strip()
    if skill_text.startswith("["):
        try:
            skills = ast.literal_eval(skill_text)
        except Exception:
            skills = re.split(r"[,;|]", skill_text)
    else:
        skills = re.split(r"[,;|]", skill_text)
    return [c for c in (clean_skill(s) for s in skills) if c]


def parse_skills_string(raw):
    """A messy skills cell -> list of cleaned skill strings."""
    if pd.isna(raw):
        return []
    text = str(raw).strip()
    if text.startswith("[") and text.endswith("]"):
        try:
            items = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            items = re.split(r"[,;|]", text.strip("[]"))
    else:
        items = re.split(r"[,;|]", text)
    return [c for c in (clean_skill(i) for i in items) if c]


def normalize_company_dataset(df):
    df = df.copy()
    df["company_name"] = df["company_name"].apply(clean_company)
    df["business_sector"] = df["business_sector"].apply(clean_sector)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def normalize_resume_jobs(df):
    df = df.copy()
    df.drop_duplicates(inplace=True)
    df["Job Title"] = df["Job Title"].apply(clean_job)
    df["Key Skills"] = df["Key Skills"].apply(parse_skills)
    df["Industry"] = df["Industry"].apply(clean_sector)
    df.reset_index(drop=True, inplace=True)
    return df


# ---------------------------------------------------------------------------
# Dataset loading + the frequency-filtered job-matching engine
# ---------------------------------------------------------------------------
# A skill only counts as "required" for a job if it appears in at least this
# share of the postings we saw for that title.
MIN_SKILL_FREQUENCY = 0.15
# Ignore job titles seen fewer than this many times — not enough postings
# to trust the stats yet.
MIN_POSTINGS = 3


import os
import glob

def _get_csv_path(dataset_dir):
    """
    Return the path to the first CSV file found inside the dataset directory.
    Searches recursively if no CSV is at the top level.
    """
    # First check top-level
    csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))
    if csv_files:
        return csv_files[0]
    # If not found, walk subdirectories
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:
            if file.endswith(".csv"):
                return os.path.join(root, file)
    raise FileNotFoundError(f"No CSV file found in {dataset_dir}")

def _ensure_datasets_loaded():
    """Download + clean the four Kaggle datasets and build the matching
    structures, once. Safe to call repeatedly (no-ops after the first)."""
    global DATASETS_LOADED, JOB_TO_INDUSTRY, COMPANY_TO_SECTOR, INDUSTRY_TO_COMPANIES
    if DATASETS_LOADED:
        return

    # Dataset 1 — company -> business sector
    csv_path1 = kagglehub.dataset_download("mariamtamer357/company-dataset")
    file1 = _get_csv_path(csv_path1)
    dataset_text1 = pd.read_csv(file1, usecols=["company_name", "business_sector"])

    # Dataset 2 — job titles & required skills
    csv_path2 = kagglehub.dataset_download("usmohamed/job-titles-and-roles-dataset-with-skills")
    file2 = _get_csv_path(csv_path2)
    dataset_text2 = pd.read_csv(
        file2,
        usecols=["job_title", "category", "experience_level", "remote", "skills_required"],
    )

    # Dataset 3 — real job postings with company + skills
    csv_path3 = kagglehub.dataset_download("wandererfakeer/data-jobs-by-lukebarousse")
    file3 = _get_csv_path(csv_path3)
    dataset_text3 = pd.read_csv(
        file3,
        usecols=["job_title_short", "job_title", "company_name", "job_skills", "job_type_skills"],
    )

    # Dataset 4 — resumes -> job titles / industry / key skills.
    csv_path4 = kagglehub.dataset_download("thedevastator/predicting-job-titles-from-resumes")
    file4 = _get_csv_path(csv_path4)
    dataset_text4 = pd.read_csv(file4, usecols=["Job Title", "Industry", "Key Skills"])

    # ... rest of the function (cleaning and matching) unchanged ...
    # --- company sector + industry lookups (dataset 1 + dataset 4) ---
    company_df = normalize_company_dataset(dataset_text1)
    for _, row in company_df.iterrows():
        company, sector = row["company_name"], row["business_sector"]
        if company and sector:
            COMPANY_TO_SECTOR[company] = sector
            INDUSTRY_TO_COMPANIES[sector].add(company)

    resume_jobs_df = normalize_resume_jobs(dataset_text4)
    for _, row in resume_jobs_df.iterrows():
        job, industry = row["Job Title"], row["Industry"]
        if job and industry:
            JOB_TO_INDUSTRY[job] = industry

    # --- frequency-filtered job -> required-skills matching ---
    job_skill_counts = defaultdict(Counter)  # job -> {skill: how many postings mention it}
    job_posting_counts = defaultdict(int)
    job_to_companies = defaultdict(set)

    def record_posting(job, skills):
        if not job:
            return
        job_posting_counts[job] += 1
        job_skill_counts[job].update(skills)

    for _, row in dataset_text2.iterrows():
        job = clean_job_title(row["job_title"])
        record_posting(job, parse_skills_string(row["skills_required"]))

    # job_title_short is already a cleaned/canonical title in this dataset
    for _, row in dataset_text3.iterrows():
        job = clean_job_title(row["job_title_short"])
        record_posting(job, parse_skills_string(row["job_skills"]))
        if job:
            company = clean_company(row["company_name"])
            if company:
                job_to_companies[job].add(company)

    for _, row in dataset_text4.iterrows():
        job = clean_job_title(row["Job Title"])
        record_posting(job, parse_skills_string(row["Key Skills"]))

    job_to_skills = {}
    for job, postings in job_posting_counts.items():
        if postings < MIN_POSTINGS:
            continue
        counts = job_skill_counts[job]
        job_to_skills[job] = {
            skill for skill, n in counts.items() if n / postings >= MIN_SKILL_FREQUENCY
        }

    skill_to_jobs = defaultdict(set)
    for job, skills in job_to_skills.items():
        for skill in skills:
            skill_to_jobs[skill].add(job)

    JOB_TO_SKILLS.update(job_to_skills)
    JOB_POSTING_COUNTS.update(job_posting_counts)
    JOB_TO_COMPANIES.update(job_to_companies)
    SKILL_TO_JOBS.update(skill_to_jobs)

    DATASETS_LOADED = True


def get_dataset_stats():
    """Live counts for the sidebar 'About' section, once datasets are loaded."""
    if not DATASETS_LOADED:
        return None
    companies = {c for comps in JOB_TO_COMPANIES.values() for c in comps}
    return {
        "skills": len(SKILL_TO_JOBS),
        "jobs": len(JOB_TO_SKILLS),
        "companies": len(companies),
    }


def _build_reason(job_title, matched, missing):
    """Fast, template-based explanation shown on each job card (no LLM call —
    keeps recommend_jobs() instant for 10 jobs at a time). See
    generate_career_advice() for the full Mistral-written report."""
    if matched:
        top = ", ".join(s.title() for s in sorted(matched)[:3])
        return f"Your experience strongly matches {job_title.title()} because of your background in {top}."
    return (
        f"{job_title.title()} could still be worth exploring, but your resume doesn't yet "
        "show the core skills this role typically requires."
    )


def recommend_jobs(skills, top_n=10):
    """
    Public entry point #2.

    Matches a list of candidate skills against the frequency-filtered
    job -> required-skills map. Returns a list of dicts (best match first):

        {
            "job": str, "score": float, "industry": str, "postings": int,
            "matched_skills": list[str], "missing_skills": list[str],
            "companies": list[str], "reason": str,
        }
    """
    _ensure_datasets_loaded()
    student_set = {clean_skill(s) for s in skills if clean_skill(s)}

    results = []
    for job, required in JOB_TO_SKILLS.items():
        if not required:
            continue
        matched = student_set & required
        missing = required - student_set
        score = round(len(matched) / len(required) * 100, 1)
        results.append(
            {
                "job": job.title(),
                "score": score,
                "industry": (JOB_TO_INDUSTRY.get(job) or "Unknown").title(),
                "postings": JOB_POSTING_COUNTS[job],
                "matched_skills": sorted(s.title() for s in matched),
                "missing_skills": sorted(s.title() for s in missing),
                "companies": [c.title() for c in sorted(JOB_TO_COMPANIES.get(job, []))[:5]],
                "reason": _build_reason(job, matched, missing),
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


# ---------------------------------------------------------------------------
# Missing-skills categorization (new — combines the same matching engine
# with a category map so Mode 3 of the UI has something to group)
# ---------------------------------------------------------------------------
SKILL_CATEGORIES = {
    "Programming Languages": {
        "python", "java", "c++", "c#", "javascript", "typescript", "go", "r",
        "kotlin", "swift", "php", "ruby", "scala",
    },
    "Cloud": {"aws", "azure", "gcp", "docker", "kubernetes"},
    "Data": {
        "sql", "spark", "pandas", "numpy", "hadoop", "sql server",
        "mongodb", "postgresql", "power bi", "excel",
    },
    "Machine Learning": {
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "artificial intelligence",
        "natural language processing", "computer vision",
    },
    "Web & Frameworks": {"react", "angular", "vue", "django", "flask", "node.js", "rest api"},
    "DevOps & Tools": {"git", "jenkins", "ci/cd", "linux", "bash"},
}


def _categorize_skill(skill):
    skill_l = skill.lower()
    for category, members in SKILL_CATEGORIES.items():
        if skill_l in members:
            return category
    return "Other"


def recommend_missing_skills(skills, top_n_jobs=10):
    """
    Public entry point #3.

    Aggregates the missing skills across the top job matches, ranks each by
    how many of those top jobs require it, and groups them into learning
    categories with a High/Medium/Low priority. Returns:

        { category_name: [ {"skill": str, "priority": str, "demand": int}, ... ] }
    """
    top_jobs = recommend_jobs(skills, top_n=top_n_jobs)

    demand = Counter()
    for job in top_jobs:
        for skill in job["missing_skills"]:
            demand[skill] += 1

    high_cutoff = max(3, top_n_jobs // 3)
    categorized = defaultdict(list)
    for skill, count in demand.items():
        if count >= high_cutoff:
            priority = "High"
        elif count >= 2:
            priority = "Medium"
        else:
            priority = "Low"
        categorized[_categorize_skill(skill)].append(
            {"skill": skill, "priority": priority, "demand": count}
        )

    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (priority_rank[x["priority"]], -x["demand"]))

    return dict(categorized)


# ---------------------------------------------------------------------------
# Optional bonus: the full Mistral-authored career-advice report, exactly as
# built in the original script (build_job_recommendation_prompt + generate_text
# + format_mistral_output). Not required by the UI spec, but wired up in
# app.py as an extra "AI Career Advisor Report" section under Job Recommendation.
# ---------------------------------------------------------------------------
def build_job_recommendation_prompt(job_recommendations, student_skills):
    """Convert recommended jobs into a prompt for Mistral."""
    prompt = f"""
You are an expert AI career advisor.

A student's extracted skills are:

{", ".join(student_skills)}

Based on a large job-market dataset, the following jobs were recommended.

"""
    for i, job in enumerate(job_recommendations, 1):
        prompt += f"""
{i}. {job['job']}
   Match Score : {job['score']}%
   Industry    : {job.get('industry', 'Unknown')}
   Job Postings: {job['postings']}

   Skills Matched:
   {', '.join(job['matched_skills']) if job['matched_skills'] else 'None'}

   Missing Skills:
   {', '.join(job['missing_skills']) if job['missing_skills'] else 'None'}
"""
    prompt += """

Please provide:

1. A short summary of the student's strengths.
2. Explain why each job is a good fit.
3. Rank the jobs from most suitable to least suitable.
4. Identify the most valuable missing skills.
5. Recommend a learning roadmap to improve employability.
6. Mention which job should be targeted first and why.

Keep the answer professional, concise, and easy for a university student to understand.
"""
    return prompt


def format_mistral_output(response):
    """Convert Mistral output into a clean, readable string."""
    if isinstance(response, list):
        response = response[0]
    response = response.replace("\\n", "\n")
    marker = "---"
    if marker in response:
        response = response.split(marker, 1)[1]
    response = response.replace("**", "")
    response = response.replace("*", "")
    response = re.sub(r"\n{3,}", "\n\n", response)
    response = re.sub(r"[ \t]+\n", "\n", response)
    return response.strip()


def generate_career_advice(top_jobs, skills):
    """Full written career-advice report from Mistral (slower — one LLM call)."""
    prompt = build_job_recommendation_prompt(top_jobs, skills)
    answer = _call_mistral_api(prompt, max_length=4500)
    return format_mistral_output(answer)