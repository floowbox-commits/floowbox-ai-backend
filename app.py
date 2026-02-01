from flask import Flask, request, jsonify
from flask_cors import CORS
import re, os

app = Flask(__name__)
CORS(app)

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    try:
        resume_text = request.json.get('resume_text', '')
        email = re.search(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}', resume_text)
        phone = re.search(r'\+?91[\s-]?[6-9]\d{9}', resume_text)
        skills_list = ['python','java','javascript','react','sql',
                       'django','html','css','nodejs','aws','excel',
                       'machine learning','data science','git']
        text_lower = resume_text.lower()
        skills = [s for s in skills_list if s in text_lower]
        exp = re.search(r'(\d+)\s*(?:years?|yrs?)', text_lower)
        experience = int(exp.group(1)) if exp else 0
        return jsonify({
            'success': True,
            'data': {
                'email': email.group() if email else None,
                'phone': phone.group() if phone else None,
                'skills': skills,
                'experience_years': experience,
                'skill_score': min(len(skills)*10, 100)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    try:
        data = request.json
        c_skills = set(data.get('candidate_skills', []))
        j_skills = set(data.get('job_skills', []))
        c_exp = data.get('candidate_experience', 0)
        r_exp = data.get('required_experience', 0)
        matched = c_skills & j_skills
        skill_pct = (len(matched)/len(j_skills)*100) if j_skills else 0
        exp_pct = 100 if c_exp >= r_exp else (c_exp/r_exp*100 if r_exp else 100)
        overall = skill_pct * 0.6 + exp_pct * 0.4
        label = "Strong Match" if overall>=80 else "Good Match" if overall>=60 else "Partial"
        return jsonify({
            'success': True,
            'data': {
                'overall_score': round(overall, 1),
                'skill_match': round(skill_pct, 1),
                'matched_skills': list(matched),
                'recommendation': label
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Floowbox AI is running!'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
