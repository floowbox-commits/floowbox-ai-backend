import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ─────────────────────────────────────────────
# ENDPOINT 1: AI Resume Parser (LLM-powered)
# ─────────────────────────────────────────────
@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    try:
        resume_text = request.json.get('resume_text', '')
        if not resume_text:
            return jsonify({'success': False, 'error': 'resume_text is required'}), 400

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": f"""You are a resume parser for Indian job seekers.
Extract the following from the resume and return ONLY a valid JSON object. No extra text, no markdown, just raw JSON.

Fields to extract:
- name (string)
- email (string or null)
- phone (string or null)
- skills (array of skill strings – be thorough, include hard and soft skills)
- experience_years (integer – infer total years of work experience)
- education (string – highest qualification)
- summary (1-2 sentence AI-generated professional summary)
- career_intent (string – what role/domain this person is best suited for)

Resume text:
---
{resume_text}
---

Return ONLY this JSON:
{{
  "name": "",
  "email": "",
  "phone": "",
  "skills": [],
  "experience_years": 0,
  "education": "",
  "summary": "",
  "career_intent": ""
}}"""
            }]
        )

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)

        # Profile completeness score
        score = 0
        if parsed.get("name"):      score += 15
        if parsed.get("email"):     score += 10
        if parsed.get("skills"):    score += min(len(parsed["skills"]) * 8, 40)
        if parsed.get("experience_years", 0) > 0: score += 15
        if parsed.get("education"): score += 10
        if parsed.get("summary"):   score += 10
        parsed["profile_score"] = min(score, 100)

        return jsonify({'success': True, 'data': parsed}), 200

    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON parse failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────
# ENDPOINT 2: AI Job Matching (LLM-powered)
# ─────────────────────────────────────────────
@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    try:
        data = request.json
        candidate = data.get('candidate', {})
        jobs = data.get('jobs', [])

        if not candidate or not jobs:
            return jsonify({'success': False, 'error': 'candidate and jobs required'}), 400

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            messages=[{
                "role": "user",
                "content": f"""You are an intelligent job-matching AI for Delhi MSMEs.

Analyze fit holistically – not just keyword matching.
Consider: skill overlap, experience relevance, career trajectory, growth potential, and cultural fit for Delhi's MSME ecosystem.

Candidate Profile:
{json.dumps(candidate, indent=2)}

Available Jobs:
{json.dumps(jobs, indent=2)}

For EACH job, produce a match analysis. Return ONLY a valid JSON array. No extra text.

[
  {{
    "job_id": "",
    "job_title": "",
    "company": "",
    "match_score": 0,
    "confidence": "",
    "matched_skills": [],
    "gaps": [],
    "ai_reasoning": "",
    "growth_potential": "",
    "recommendation": ""
  }}
]

Sort by match_score descending."""
            }]
        )

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        matches = json.loads(raw)

        return jsonify({'success': True, 'data': matches, 'total_jobs_analyzed': len(matches)}), 200

    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'JSON parse failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────
# ENDPOINT 3: Health Check
# ─────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'Floowbox AI Agent is live!',
        'model': 'claude-haiku-4-5-20251001',
        'powered_by': 'Anthropic Claude API',
        'capabilities': ['resume_parsing', 'job_matching', 'skill_gap_analysis']
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
