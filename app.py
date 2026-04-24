from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, render_template, request

from services.file_parser import extract_resume_text
from services.llm_client import LLMClient, LLMError

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

llm = LLMClient(base_dir=BASE_DIR)


@app.get("/")
def home():
    sample_jobs = [
        (BASE_DIR / "sample_data" / "job_1_python_backend.txt").read_text(encoding="utf-8"),
        (BASE_DIR / "sample_data" / "job_2_data_analyst.txt").read_text(encoding="utf-8"),
        (BASE_DIR / "sample_data" / "job_3_ml_intern.txt").read_text(encoding="utf-8"),
    ]
    return render_template("index.html", sample_jobs=sample_jobs)


@app.post("/analyze")
def analyze():
    try:
        resume_text = extract_resume_text(request)

        jobs = []
        for key in ["job_1", "job_2", "job_3"]:
            value = (request.form.get(key) or "").strip()
            if value:
                jobs.append(value)

        extra_job = (request.form.get("custom_job") or "").strip()
        if extra_job:
            jobs.append(extra_job)

        if not jobs:
            return render_template("error.html", message="Please provide at least one job description."), 400

        result = llm.analyze_resume_against_jobs(resume_text=resume_text, jobs=jobs)

        return render_template(
            "result.html",
            raw_resume=resume_text,
            result=result,
            json_preview=json.dumps(result, indent=2),
        )
    except LLMError as exc:
        return render_template("error.html", message=str(exc)), 400
    except ValueError as exc:
        return render_template("error.html", message=str(exc)), 400
    except Exception:
        return render_template("error.html", message="Unexpected error. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=True)
