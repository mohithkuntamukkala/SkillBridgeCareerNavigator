from openai_agent import OpenAIAgent

import json
import re
import random

def safe_generate(agent, prompt):
    try:
        out = agent.generate(prompt)
        return {"status": "ok", "data": out}
    except Exception as e:
        return {
            "status": "api_error",
            "error": str(e)
        }
    
def is_valid_json(output):
    try:
        json.loads(output) if isinstance(output, str) else output
        return True
    except:
        return False

class RoadMapAgent(OpenAIAgent):
    def __init__(self, model_slug, api_key,role):
        super().__init__(model_slug, api_key)
        self.role = role
        self.base_prompt = """You are an expert career mentor and curriculum designer.

Your task is to generate a personalized learning roadmap based on:
1. Target ROLE
2. Missing skills JSON

The roadmap must strongly focus on:
- Closing CORE skill gaps (highest priority)
- Incorporing BONUS skills (secondary priority)
- Aligning everything with real-world expectations of the ROLE

---

### INPUT:
ROLE:
{role}

MISSING_SKILLS_JSON:
{missing_skills}

Where missing_skills is in the format:
{{
  "core_missing": [list of critical missing skills],
  "bonus_skills": [list of optional or good-to-have skills]
}}

---

### INSTRUCTIONS:

1. Prioritize CORE skills over BONUS skills.
2. Group learning into logical phases (beginner → intermediate → advanced).
3. Ensure the roadmap is practical and implementation-focused.
4. Include:
   - Hands-on tasks
   - Real-world projects
   - Industry-relevant tools
5. Avoid generic advice. Be specific to the ROLE.
6. Keep output concise but meaningful.
7. Do NOT include any explanations outside JSON.

---

### OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "learning_path": [steps],
  "projects": [projects],
  "resources": [resource/course]
}}

---

### CONSTRAINTS:

- Do NOT hallucinate irrelevant skills
- Do NOT repeat skills unnecessarily
- Ensure every project maps to at least one missing skill
- Ensure learning_path progressively builds toward projects
- Prefer modern tools and frameworks relevant to {role}

---

Now generate the roadmap."""

    def run(self,missing_skills):
        curr_prompt = self.base_prompt.format(role = self.role,missing_skills = missing_skills)

        response = safe_generate(self, 'Test')
        print(response)
        if not response['status'] == 'ok':
            return fallback_roadmap(self.role)

        out = super().generate_json(curr_prompt,{'learning_path':[],'projects':[],'resources':[]})

        try:
            parsed = out
            if "learning_path" not in parsed or "projects" not in parsed or "resources" not in parsed:
                return fallback_roadmap(self.role)
            return parsed
        except:
            return fallback_roadmap(self.role)

def fallback_roadmap(role):
    with open('data/roadmaps.json') as f:
        roadmaps = json.load(f)
    return roadmaps[role]

class MockInterviewAgent(OpenAIAgent):
    def __init__(self, model_slug, api_key,role):
        super().__init__(model_slug, api_key)
        self.role = role
        self.base_prompt = """You are an expert technical interviewer.

Your task is to generate mock interview questions tailored to:
1. Target ROLE
2. Candidate's existing SKILLS (from resume) if there are no existing skills some basic questions on programming 

The goal is to simulate a realistic interview that:
- Focuses on the ROLE requirements
- Tests the candidate’s actual SKILLS in depth
- Includes a mix of conceptual, practical, and problem-solving questions

---

### INPUT:

ROLE:
{role}

CANDIDATE_SKILLS_JSON:
{skills_json}

Where skills_json is in the format:
{{
  "skills": [list of skills from resume]
}}

---

### INSTRUCTIONS:

1. Generate a diverse set of questions including:
   - Core theoretical questions
   - Practical implementation questions
   - Scenario-based / real-world questions
   - Coding or problem-solving questions (if relevant to role)

2. Strongly align questions with:
   - The ROLE expectations
   - The candidate's listed SKILLS

3. Prioritize depth over breadth:
   - Ask questions that probe understanding of listed skills
   - Avoid generic or unrelated questions

4. Include varying difficulty levels:
   - Easy (fundamentals)
   - Medium (applied knowledge)
   - Hard (advanced / edge cases / system thinking)

5. Ensure:
   - Each question clearly maps to at least one skill
   - No repeated or redundant questions
   - Questions feel like real interview questions from industry

6. Keep questions concise and clear.

7. Do NOT include answers or explanations.

8. If the candidate has no skills/ a lack of skills generate basic questions on programming

---

### OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "questions": [question1,question2,...]
}}

---

### CONSTRAINTS:

- Do NOT hallucinate skills not present in input
- Do NOT generate overly generic questions
- Ensure good coverage of all provided skills
- Prefer role-relevant tools, frameworks, and patterns

---

Now generate the mock interview questions."""

    def run(self,skills):
        curr_prompt = self.base_prompt.format(role = self.role,skills_json = skills)

        response = safe_generate(self, 'Test')
        print(response)
        if not response['status'] == 'ok':
            return fallback_interview(skills)

        out = super().generate_json(curr_prompt,{'questions': []})

        try:
            parsed = out
            if "questions" not in parsed:
                return fallback_interview(skills)
            return parsed
        except:
            return fallback_interview(skills)
        
def fallback_interview(skills):
    print(skills)
    if not skills:
        with open('data/interview_questions.json') as f:
             questions = json.load(f)
        question_bank = []
        for skill in ['python','java','sql','git','go','javascript','r']:
            question_bank.extend(questions[skill]['questions'])
        return {'questions':random.sample(question_bank,12)}
        
    
    with open('data/interview_questions.json') as f:
        questions = json.load(f)
    print(questions)
    question_bank = []
    if isinstance(skills,dict):
        skills = skills['skills']
    for skill in skills:
        if skill in questions:
            question_bank.extend(questions[skill]['questions'])
    print(question_bank)
    return {'questions':random.sample(question_bank,min(len(question_bank),12))}
    
        
        