# Simplified LLM Resume Analyzer - Complete Project Guide

## 1) Project Purpose

This project is a **minimal Flask web app** that analyzes a resume against multiple job descriptions.

Unlike hybrid NLP systems, this version intentionally uses an LLM for almost all intelligence tasks:
- resume parsing
- match scoring
- skill gap analysis
- suggestions
- summary rewriting
- ranking across jobs

The app focuses on clarity and fast local setup for students.

---

## 2) Folder Structure and File Roles

```text
simplified_llm_resume_analyzer/
  app.py
  requirements.txt
  .env.example
  README.md
  PROJECT_GUIDE.md
  services/
    file_parser.py
    llm_client.py
  templates/
    base.html
    index.html
    result.html
    error.html
  static/
    css/style.css
    js/main.js
  sample_data/
    job_1_python_backend.txt
    job_2_data_analyst.txt
    job_3_ml_intern.txt
```

### Core files
- `app.py`: Flask app, routes, request handling, rendering pages.
- `services/file_parser.py`: handles resume extraction from TXT/PDF/pasted text.
- `services/llm_client.py`: Hugging Face API integration and LLM prompting logic.
- `templates/index.html`: input page (resume + jobs).
- `templates/result.html`: output page with parsed data, scores, ranking, suggestions.
- `templates/error.html`: user-friendly error display.

---

## 3) End-to-End Working Flow

## Step A: User opens home page
Route: `GET /`
- App loads sample job descriptions from `sample_data/*.txt`.
- Renders `index.html` with prefilled job text areas.

## Step B: User submits analysis form
Route: `POST /analyze`
- App gets resume from either upload or pasted text.
- App collects job descriptions (`job_1`, `job_2`, `job_3`, optional `custom_job`).
- App calls `LLMClient.analyze_resume_against_jobs(...)`.

## Step C: LLM returns structured JSON
- App validates required keys in JSON.
- App renders `result.html` with analysis sections.

## Step D: If anything fails
- App renders `error.html` with clear reason (missing key, bad file, API error, etc.).

---

## 4) Detailed Code Walkthrough

## 4.1 `app.py`

Responsibilities:
- Initializes Flask app with explicit template/static folders.
- Creates one `LLMClient` instance.
- Defines two main routes:
  - `GET /`
  - `POST /analyze`

Why this design:
- Keeps entrypoint small and readable.
- Delegates parsing and LLM responsibilities to service modules.

Important behavior:
- `MAX_CONTENT_LENGTH = 5 MB` for safer uploads.
- All exceptions are handled and shown via `error.html`.

## 4.2 `services/file_parser.py`

Responsibilities:
- Validates upload type (`pdf`, `txt`).
- Handles text extraction:
  - TXT: UTF-8 decode
  - PDF: `PyPDF2.PdfReader` page extraction
- Supports fallback to pasted text if provided.

Why this design:
- Beginner-friendly, minimal dependencies.
- Keeps file/format logic separate from web route code.

## 4.3 `services/llm_client.py`

Responsibilities:
- Loads env config (`HF_API_KEY`, `HF_BASE_URL`, `HF_MODEL`).
- Builds prompt containing resume + all jobs.
- Calls Hugging Face `chat/completions` endpoint.
- Parses and validates JSON response.

Why this design:
- Single place for all LLM behavior.
- Easy to swap provider/model later without touching routes/templates.

---

## 5) Where, How, and Why LLM is Used

This is the most important part of the project.

## 5.1 Where LLM is used
The LLM is used in exactly one place in the backend:
- `LLMClient.analyze_resume_against_jobs()` in `services/llm_client.py`

From that single call, the LLM performs:
1. Resume parsing
2. Skill extraction
3. Job-wise score calculation
4. Matched vs missing skills
5. Strength/weakness explanation
6. ATS suggestions
7. Rewritten summary
8. Ranking multiple jobs
9. Overall quick wins and major gaps

## 5.2 How LLM is used
The app sends a **structured prompt** containing:
- Resume text
- Multiple job descriptions
- Strict JSON schema requirements
- Rules on scoring consistency and concise output

The app requests JSON output using response formatting and then validates required top-level fields:
- `parsed_resume`
- `job_analysis`
- `ranked_jobs`
- `overall_feedback`

If output is missing fields or invalid JSON, app raises an explicit `LLMError`.

## 5.3 Why LLM is used here
This simplified project intentionally chooses LLM-first behavior to reduce engineering complexity.

Benefits:
- Very small codebase
- Fast feature delivery
- Flexible across diverse resume/job formats
- Minimal handcrafted NLP logic

Trade-offs:
- Output quality depends on model quality
- Needs network + API key
- Costs and latency depend on provider/model
- Less deterministic than rule-based pipelines

This trade-off is acceptable for a beginner project focused on rapid prototyping and demonstration.

---

## 6) JSON Output Contract (Expected from LLM)

Top-level keys required:
- `parsed_resume`
- `job_analysis`
- `ranked_jobs`
- `overall_feedback`

### Example logical shape
```json
{
  "parsed_resume": {
    "name": "...",
    "email": "...",
    "phone": "...",
    "education": [],
    "skills": [],
    "projects": [],
    "work_experience": []
  },
  "job_analysis": [
    {
      "job_index": 1,
      "match_score": 78,
      "matched_skills": [],
      "missing_skills": [],
      "strengths": [],
      "weaknesses": [],
      "ats_suggestions": [],
      "rewritten_summary": "..."
    }
  ],
  "ranked_jobs": [
    {"job_index": 1, "match_score": 78, "reason": "..."}
  ],
  "overall_feedback": {
    "quick_wins": [],
    "major_gaps": []
  }
}
```

---

## 7) Hugging Face Integration Details

Environment variables:
- `HF_API_KEY`
- `HF_BASE_URL` (default: `https://router.huggingface.co/v1`)
- `HF_MODEL` (default: `meta-llama/Llama-3.1-8B-Instruct`)

HTTP call:
- Endpoint: `POST {HF_BASE_URL}/chat/completions`
- Headers:
  - `Authorization: Bearer <HF_API_KEY>`
  - `Content-Type: application/json`
- Body includes:
  - `model`
  - `messages`
  - `temperature`
  - JSON output instruction

Common API error:
- `insufficient permissions to call Inference Providers`

Fix:
- Create/edit HF token with Inference Provider permissions.

---

## 8) Frontend Behavior

## `index.html`
- Resume upload input
- Resume paste textarea
- Three job textareas (prefilled)
- Optional custom job textarea
- Submit button

## `result.html`
Displays:
- Parsed resume details
- Ranked jobs
- Per-job analysis blocks
- Overall feedback
- Raw JSON preview for debugging and transparency

## `error.html`
- Shows clear, human-readable message
- Provides navigation back to home page

---

## 9) Why This Design is Beginner-Friendly

- Only 2 backend services (`file_parser`, `llm_client`)
- One primary analysis route
- Very small dependency list
- Simple HTML templates without JS framework complexity
- Clear failure modes with readable error messages

---

## 10) Security and Reliability Notes

- API key is read from `.env`; never hardcode in code.
- Uploaded files are size-limited (5 MB).
- PDF extraction may fail for scanned/image PDFs.
- LLM output is validated but still model-dependent.

Recommended improvements:
- Add retry + fallback model logic.
- Add rate-limit handling.
- Add persistent logging.
- Add unit tests for parser and LLM response validation.

---

## 11) How to Run

```bash
cd simplified_llm_resume_analyzer
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill HF_API_KEY in .env
python app.py
```

Open: `http://127.0.0.1:5000`

---

## 12) Summary

This project is a clean **LLM-first resume analyzer**.
It keeps code simple by centralizing all intelligence in one model call while preserving enough backend structure for maintainability.

If you want, next step can be a second document with diagrams (request flow + sequence + architecture) for PPT submission.
