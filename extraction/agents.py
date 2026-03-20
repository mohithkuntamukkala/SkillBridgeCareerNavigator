from openai_agent import OpenAIAgent
import json
import re

def extract_json(text):
    if not text:
        return {}

    # 1. Try direct parse
    try:
        return json.loads(text)
    except:
        pass

    # 2. Remove markdown ```json ``` wrappers
    cleaned = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(cleaned)
    except:
        pass

    # 3. Extract first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        json_str = match.group()
        try:
            return json.loads(json_str)
        except:
            pass

    # 4. Extract first [...] block (in case top-level is list)
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        json_str = match.group()
        try:
            return json.loads(json_str)
        except:
            pass

    # 5. Fallback
    print("❌ Failed to parse JSON. Raw output:")
    print(text)
    return {}

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

class SkillExtractionAgent(OpenAIAgent):
    def __init__(self, model_slug, api_key, role):
        super().__init__(model_slug, api_key)
        self.role = role

        self.base_prompt = """You are an expert resume parser.

Extract ALL skills mentioned in the resume text below.

Instructions:
- Include technical skills, programming languages, frameworks, tools, libraries, and relevant concepts
- Do NOT include soft skills
- Do NOT hallucinate
- Normalize skills (e.g., "python" → "Python")
- Remove duplicates

Return ONLY valid JSON:
{{"skills": ["skill1", "skill2"]}}

Resume:
{resume_text}
"""

    def run(self, text):
        prompt = self.base_prompt.format(resume_text=text)
        response = safe_generate(self, 'Test')
        print(response)
        if not response['status'] == 'ok':
            print('fallback')
            return fallback_skills(text,self.role)
        output = self.generate_json(prompt,{"skills":[]})
        #print(output)
        if not output:
            print('fallback')
            #print('llm error')
            return fallback_skills(text, self.role)
        # try:
        #     parsed = json.loads(output)
        # except:
        #     print('json parse error')
        #     return fallback_skills(text, self.role)
        if "skills" not in output:
            print('fallback')
            #print('wrong json schema')
            return fallback_skills(text, self.role)

        return output
    
def fallback_skills(text,role):
    with open('data/roles_data.json') as f:
        role_data = json.load(f)
    skills = set(role_data[role]['skills'])
    found = set()
    for word in text.split(' '):
        if word.lower() in skills:
            found.add(word.lower())
    return {'skills': list(found)}

class ProjectExtractionAgent(OpenAIAgent):
    def __init__(self, model_slug, api_key):
        super().__init__(model_slug, api_key)

        self.base_prompt = """You are an expert resume parser.

Extract ALL projects from the resume.

Instructions:
- Extract project names
- Include short description if available
- Do NOT hallucinate
- Keep entries concise

Return ONLY valid JSON:
{{"projects": ["project1", "project2"]}}

Resume:
{resume_text}
"""

    def run(self, text):
        curr_prompt = self.base_prompt.format(resume_text=text)

        response = safe_generate(self, 'Test')
        if not response['status'] == 'ok':
            return fallback_projects(text)

        out = super().generate_json(curr_prompt,{'projects':[]})
        print(type(out))
        if isinstance(out,str):
            out = extract_json(out)
        print(out)

        try:
            parsed = out
            if "projects" not in parsed:
                return fallback_projects(text)
            return parsed
        except:
            return fallback_projects(text)

def fallback_projects(text):
    lines = text.split("\n")

    project_keywords = ["project", "built", "developed", "created", "designed"]

    projects = []

    for line in lines:
        l = line.lower()

        if any(k in l for k in project_keywords):
            projects.append(line.strip())

    # remove noise (very short lines)
    projects = [p for p in projects if len(p) > 10]

    if not projects:
        return {"projects": []}

    # deduplicate
    return {"projects": list(set(projects))}

class ExperienceExtractionAgent(OpenAIAgent):
    def __init__(self, model_slug, api_key):
        super().__init__(model_slug, api_key)

        self.base_prompt = """You are an expert resume parser.

Extract ALL work experience AND education details from the resume.

Instructions:
- Include job roles, companies, durations, responsibilities
- Include education (degree, university, year if present)
- Combine everything into a clean, structured paragraph
- Do NOT hallucinate
- Keep it concise but complete

Return ONLY valid JSON:
{{"experience": "full experience description here"}}

Resume:
{resume_text}
"""

    def run(self, text):
        curr_prompt = self.base_prompt.format(resume_text=text)

        response = safe_generate(self, 'Test')
        if not response['status'] == 'ok':
            return fallback_experience(text)

        out = super().generate_json(curr_prompt,{'experience':''})

        try:
            parsed = out
            if "experience" not in parsed or not parsed["experience"]:
                return fallback_experience(text)
            return parsed
        except:
            return fallback_experience(text)

def fallback_experience(text):
    text_lower = text.lower()

    lines = text.split("\n")

    exp_keywords = ["experience", "worked", "intern", "engineer", "developer"]
    edu_keywords = ["b.tech", "m.tech", "bachelor", "master", "phd", "university", "college"]

    extracted = []

    for line in lines:
        l = line.lower()

        if any(k in l for k in exp_keywords) or any(k in l for k in edu_keywords):
            extracted.append(line.strip())

    if not extracted:
        # fallback fallback (last safety)
        return {"experience": text[:500]}

    return {"experience": " ".join(extracted)}

class ProfileExtractor():
    def __init__(self,model_slug,api_key,role):
        self.skill_extractor = SkillExtractionAgent(model_slug,api_key,role)
        self.project_extractor = ProjectExtractionAgent(model_slug,api_key)
        self.experience_extractor = ExperienceExtractionAgent(model_slug,api_key)
    def run(self,text):
        return {'skills': self.skill_extractor.run(text)['skills'],
        'projects': self.project_extractor.run(text)['projects'],
        'experience': self.experience_extractor.run(text)['experience']}