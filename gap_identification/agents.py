from openai_agent import OpenAIAgent

import json
import re


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

class GapIdentifierAgent(OpenAIAgent):
    def __init__(self, model_slug, api_key,role):
        super().__init__(model_slug, api_key)
        self.role = role
        self.base_prompt = """You are an expert skill gap analyzer.

Identify missing skills by comparing a candidate profile with multiple job descriptions.

Instructions:
- Extract all technical skills, tools, frameworks, and concepts from the job descriptions
- Ignore generic soft skills unless critical
- Normalize skills (lowercase, merge similar terms like "torch" → "pytorch")
- Compare with candidate profile skills
- Infer skills from projects and experience ONLY if clearly evident
- Do NOT mark equivalent skills as missing
- Do NOT hallucinate any skills

Categorization rules:
- core_missing → appears in ≥ 50 percent of job descriptions
- bonus_skills → not in core_missing

If candidate has equivalent skill (e.g., "tensorflow" vs "deep learning"), consider it covered.

Return ONLY valid JSON:
{{
  "core_missing": [...],
  "bonus_skills": [...]
}}

Input:
Profile:
{profile_json}

Job Descriptions:
{jd_list}"""

    def run(self,profile_json):
        with open('data/roles_data.json') as f:
            roles_data = json.load(f)
        jds = roles_data[self.role]['job_descriptions']
        curr_prompt = self.base_prompt.format(profile_json = profile_json,jd_list = jds)

        response = safe_generate(self, 'Test')
        print(response)
        if not response['status'] == 'ok':
            return fallback_gap_identification(profile_json,self.role)

        out = super().generate_json(curr_prompt,{'core_missing':[],'bonus_skills':[]})

        try:
            parsed = out
            if "core_missing" not in parsed or "bonus_skills" not in parsed:
                return fallback_gap_identification(profile_json,self.role)
            return parsed
        except:
            return fallback_gap_identification(profile_json,self.role)
import collections

def fallback_gap_identification(profile_json,role):
    with open('data/roles_data.json') as f:
        roles_data = json.load(f)
    jds = roles_data[role]['job_descriptions']
    skills = roles_data[role]['skills']
    skills_freq = [skill.lower() for skill in skills]
    for jd in jds:
        n = jd['preferred_skills'] + jd['tech_stack']
        n = [x.lower() for x in n]
        skills_freq.extend(n)
    skills_freq = collections.Counter(skills_freq)
    core_missing,bonus = [],[]
    for skill in skills_freq:
        if skills_freq[skill]>=(len(jds)//2):
            core_missing.append(skill)
        else:
            bonus.append(skill)
    core_missing,bonus = set(core_missing),set(bonus)
    for skill in profile_json['skills']:
        if skill.lower() in core_missing:
            core_missing.remove(skill.lower())
            #print(skill.lower())
        if skill.lower() in bonus:
            bonus.remove(skill.lower())
            #print(skill.lower())
    return {'core_missing':list(core_missing),'bonus_skills':list(bonus)}