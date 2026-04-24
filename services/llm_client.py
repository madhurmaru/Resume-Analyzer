from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, base_dir: Path):
        load_dotenv(base_dir / ".env")
        self.api_key = os.getenv("HF_API_KEY", "").strip()
        self.base_url = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1").rstrip("/")
        self.model = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

    def analyze_resume_against_jobs(self, resume_text: str, jobs: list[str]) -> dict:
        if not self.api_key:
            raise LLMError(
                "HF_API_KEY is missing. Add it in simplified_llm_resume_analyzer/.env, then retry."
            )

        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert ATS resume analyzer. Return only valid JSON. "
                        "You must do parsing, scoring, missing skills, strengths, weaknesses, "
                        "resume improvement suggestions, rewritten summary, and ranking across jobs."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(resume_text, jobs),
                },
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            r.raise_for_status()
            content = self._extract_content(r.json())
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part) for part in content
                )
            if not isinstance(content, str):
                content = str(content)
            content = content.strip()
            if content.startswith("```"):
                content = content.strip("`")
                content = content.replace("json", "", 1).strip()
            result = json.loads(content)
            self._validate(result)
            return result
        except requests.HTTPError as exc:
            body = ""
            try:
                body = exc.response.text[:500]
            except Exception:
                pass
            raise LLMError(f"LLM API request failed: {body or str(exc)}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError("LLM did not return valid JSON.") from exc
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("LLM analysis failed unexpectedly.") from exc

    @staticmethod
    def _build_prompt(resume_text: str, jobs: list[str]) -> str:
        job_block = "\n\n".join([f"JOB_{i+1}:\n{job}" for i, job in enumerate(jobs)])
        return f"""
Analyze this resume against the provided jobs.

RESUME:
{resume_text[:12000]}

JOBS:
{job_block[:12000]}

Return STRICT JSON with exactly these top-level keys:
- parsed_resume: object with keys name, email, phone, education (array), skills (array), projects (array), work_experience (array)
- job_analysis: array where each item has
  - job_index (1-based)
  - match_score (0-100)
  - matched_skills (array)
  - missing_skills (array)
  - strengths (array)
  - weaknesses (array)
  - ats_suggestions (array of concise bullets)
  - rewritten_summary (3-4 lines)
- ranked_jobs: array sorted best-to-worst, each item has job_index, match_score, reason
- overall_feedback: object with quick_wins (array), major_gaps (array)

Rules:
- Scores must be realistic and internally consistent.
- Missing skills should be specific keywords from job text.
- Keep arrays concise and practical for students.
""".strip()

    @staticmethod
    def _validate(result: dict) -> None:
        required = {"parsed_resume", "job_analysis", "ranked_jobs", "overall_feedback"}
        missing = required - set(result.keys())
        if missing:
            raise LLMError(f"LLM response missing fields: {sorted(missing)}")

    @staticmethod
    def _extract_content(response_json: dict):
        try:
            return response_json["choices"][0]["message"]["content"]
        except Exception as exc:
            raise LLMError("Unexpected Hugging Face response format from /chat/completions.") from exc
