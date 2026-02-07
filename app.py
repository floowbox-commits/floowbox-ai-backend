import os, json, re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# MOCK AI HELPERS - simulate Claude responses
# ─────────────────────────────────────────────

def mock_parse_resume(resume_text):
    """Simulate AI resume parsing with smart extraction"""
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}', resume_text)
    email = email_match.group() if email_match else None
    
    # Extract phone
    phone_match = re.search(r'\+?91[\s-]?[6-9]\d{9}', resume_text)
    phone = phone_match.group() if phone_match else None
    
    # Extract name (first capitalized words)
    name_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', resume_text)
    name = name_match.group(1) if name_match else "Candidate"
    
    # Smart skill extraction with context
    skill_keywords = {
        'python': ['python', 'django', 'flask', 'fastapi'],
        'javascript': ['javascript', 'js', 'react', 'node', 'vue', 'angular'],
        'java': ['java', 'spring', 'hibernate'],
        'data': ['sql', 'mysql', 'postgresql', 'mongodb', 'data'],
        'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'],
        'frontend': ['html', 'css', 'react', 'vue', 'angular', 'frontend'],
        'backend': ['backend', 'api', 'microservices', 'rest'],
        'ml': ['machine learning', 'ml', 'ai', 'deep learning', 'tensorflow'],
    }
    
    text_lower = resume_text.lower()
    skills = []
    
    # Extract skills based on keywords
    for category, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword in text_lower and keyword.title() not in skills:
                skills.append(keyword.title())
    
    # Add inferred skills based on context
    if 'developer' in text_lower or 'engineer' in text_lower:
        if 'Python' in skills and 'Django' not in skills:
            skills.append('REST APIs')
        if any(s in skills for s in ['React', 'Vue', 'Angular']):
            skills.append('Frontend Development')
    
    if 'microservices' in text_lower:
        skills.append('Microservices Architecture')
    
    if 'flipkart' in text_lower or 'amazon' in text_lower:
        skills.append('E-commerce Systems')
    
    # Extract experience years
    exp_match = re.search(r'(\d+)\s*(?:years?|yrs?)', text_lower)
    experience_years = int(exp_match.group(1)) if exp_match else 0
    
    # Extract education
    education = None
    if 'mba' in text_lower:
        education = 'MBA'
    elif 'btech' in text_lower or 'b.tech' in text_lower:
        education = 'B.Tech'
    elif 'mtech' in text_lower:
        education = 'M.Tech'
    elif 'degree' in text_lower:
        education = 'Graduate'
    
    # Generate AI-like summary
    summary = f"{'Experienced' if experience_years >= 3 else 'Skilled'} professional with {experience_years} years in software development"
    if skills:
        summary += f", specializing in {', '.join(skills[:3])}"
    if education:
        summary += f". {education} qualified"
    summary += "."
    
    # Infer career intent
    career_intent = "Software Development"
    if 'full-stack' in text_lower or 'fullstack' in text_lower:
        career_intent = "Full-Stack Development"
    elif 'product' in text_lower:
        career_intent = "Product Development"
    elif 'backend' in text_lower:
        career_intent = "Backend Engineering"
    elif 'frontend' in text_lower:
        career_intent = "Frontend Engineering"
    elif 'data' in text_lower or 'ml' in text_lower:
        career_intent = "Data Science / ML"
    
    # Calculate profile score
    score = 0
    if name and name != "Candidate": score += 15
    if email: score += 10
    if phone: score += 5
    if skills: score += min(len(skills) * 5, 40)
    if experience_years > 0: score += min(experience_years * 5, 20)
    if education: score += 10
    
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'skills': skills[:10],  # limit to top 10
        'experience_years': experience_years,
        'education': education,
        'summary': summary,
        'career_intent': career_intent,
        'profile_score': min(score, 100)
    }


def mock_match_jobs(candidate, jobs):
    """Simulate AI job matching with intelligent reasoning"""
    
    matches = []
    c_skills = set([s.lower() for s in candidate.get('skills', [])])
    c_exp = candidate.get('experience_years', 0)
    
    for job in jobs:
        j_skills = set([s.lower() for s in job.get('required_skills', [])])
        j_exp = job.get('exp_required', 0)
        
        # Calculate matches
        matched_skills = c_skills & j_skills
        gap_skills = j_skills - c_skills
        
        # Smart scoring
        skill_match_pct = (len(matched_skills) / len(j_skills) * 100) if j_skills else 0
        
        # Experience scoring
        if c_exp >= j_exp:
            exp_score = 100
        elif c_exp >= j_exp - 1:
            exp_score = 80
        else:
            exp_score = max(0, (c_exp / j_exp * 100)) if j_exp else 100
        
        # Overall score (60% skills, 40% experience)
        overall = skill_match_pct * 0.6 + exp_score * 0.4
        
        # Generate AI reasoning
        if overall >= 80:
            reasoning = f"Strong alignment between candidate's {', '.join(list(matched_skills)[:2])} expertise and role requirements. "
            if c_exp > j_exp:
                reasoning += f"Exceeds experience requirement by {c_exp - j_exp} year(s). "
            reasoning += "High probability of immediate impact."
            recommendation = "Strong Match"
            confidence = "High"
            growth = "Medium"
        elif overall >= 60:
            reasoning = f"Good foundational match with {len(matched_skills)} overlapping skills. "
            if gap_skills:
                reasoning += f"Minor gaps in {', '.join(list(gap_skills)[:2])} can be bridged quickly. "
            reasoning += "Solid candidate with growth potential."
            recommendation = "Good Match"
            confidence = "Medium"
            growth = "High"
        else:
            reasoning = f"Partial overlap in core skills. "
            if gap_skills:
                reasoning += f"Significant gaps in {', '.join(list(gap_skills)[:2])}. "
            reasoning += "Would require substantial upskilling but shows potential."
            recommendation = "Stretch Role"
            confidence = "Low"
            growth = "High"
        
        matches.append({
            'job_id': job.get('job_id', ''),
            'job_title': job.get('title', ''),
            'company': job.get('company', ''),
            'match_score': round(overall, 1),
            'confidence': confidence,
            'matched_skills': list(matched_skills),
            'gaps': list(gap_skills),
            'ai_reasoning': reasoning,
            'growth_potential': growth,
            'recommendation': recommendation
        })
    
    # Sort by match score
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    try:
        resume_text = request.json.get('resume_text', '')
        if not resume_text:
            return jsonify({'success': False, 'error': 'resume_text required'}), 400
        
        parsed = mock_parse_resume(resume_text)
        
        return jsonify({
            'success': True,
            'data': parsed,
            'note': 'Mock AI - simulates Claude LLM behavior for demo'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    try:
        data = request.json
        candidate = data.get('candidate', {})
        jobs = data.get('jobs', [])
        
        if not candidate or not jobs:
            return jsonify({'success': False, 'error': 'candidate and jobs required'}), 400
        
        matches = mock_match_jobs(candidate, jobs)
        
        return jsonify({
            'success': True,
            'data': matches,
            'total_jobs_analyzed': len(matches),
            'note': 'Mock AI - simulates Claude LLM behavior for demo'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'Floowbox AI Agent is live!',
        'model': 'Mock AI (Claude LLM simulation)',
        'mode': 'Demo Mode - No API key required',
        'capabilities': ['resume_parsing', 'job_matching', 'skill_gap_analysis']
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
