# Simplified LLM Resume Analyzer

This is a minimal version of the project where the LLM does almost everything:
- resume parsing
- scoring
- missing skill analysis
- comparison across multiple job descriptions
- rewritten summary and ATS suggestions

## Setup

1. Open terminal in this folder:
```bash
cd simplified_llm_resume_analyzer
```

2. Create venv and install:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
```
Add your API key in `.env`:
```env
HF_API_KEY=your_huggingface_token_here
# Optional (defaults shown)
HF_BASE_URL=https://router.huggingface.co/v1
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

4. Run:
```bash
python app.py
```
Open http://127.0.0.1:5000

## Notes
- If no API key is set, the app will show a clear error.
- Use PDF/TXT upload or paste resume text.
- You can analyze against 3 prefilled sample jobs and optional extra job.
- This app uses Hugging Face Inference `chat/completions` endpoint.
