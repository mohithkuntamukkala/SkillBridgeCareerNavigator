# Candidate name
 K.Mohith
 22bcs121

# Demo Url
https://youtu.be/4zzx61lKUiI?si=zQcoT2wscjUGFtdM

# Scenario chosen

# Skill Bridge Career Navigator

## Key Capabilities

### 1. Multi-Source Profile Extraction

* Accepts:

  * PDF resumes
  * Raw text input
  * GitHub repository links
* Extracts structured data:

  * Skills (categorized)
  * Projects
  * Experience

This enables consistent downstream processing regardless of input format.

---

### 2. Skill Gap Identification

* Compares extracted user profile against role-specific requirements
* Outputs:

  * Core missing skills (critical for role readiness)
  * Secondary or bonus skills

This module is grounded in predefined role data, ensuring deterministic alignment with job expectations.

---

### 3. Personalized Roadmap Generation

* Produces:

  * Learning sequence
  * Recommended projects
  * Resource suggestions
* Tailored to:

  * User’s current skills
  * Target role requirements

The roadmap emphasizes execution and project-based learning rather than generic recommendations.

---

### 4. Mock Interview Generation

* Generates questions based on:

  * Extracted user skills
  * Target role expectations
* Focus:

  * Technical depth
  * Practical application

This ensures relevance and avoids generic question banks.

---

## System Architecture

The system follows a modular agent-based architecture:

```
Input Layer (PDF / Text / GitHub)
        ↓
Profile Extraction Agent
        ↓
Skill Gap Identification Agent
        ↓
Roadmap Generation Agent
        ↓
Mock Interview Agent
```


## Project Structure

```
.
├── app.py                     # Streamlit application entry point
├── base.py                   # Base agent abstraction
├── openai_agent.py           # OpenAI agent wrapper
│
├── extraction/
│   └── agents.py             # Profile extraction logic
│
├── gap_identification/
│   └── agents.py             # Skill comparison and gap detection
│
├── planning/
│   └── agents.py             # Roadmap generation
│
├── data/
│   ├── roles_data.json       # Role definitions and required skills
│   ├── roadmaps.json         # Reference roadmap structures
│   ├── interview_questions.json
│   └── roles.txt
```

---

## Data Flow

1. User provides input (resume / text / GitHub)
2. Text is consolidated into a unified representation
3. Profile Extraction Agent structures the data
4. Gap Identification Agent compares against role data
5. Roadmap Agent generates a learning plan
6. Interview Agent produces tailored questions

---

## Setup Instructions

### 1. Clone Repository

```
git clone <repository-url>
cd skill-bridge-navigator
```

### 2. Create Virtual Environment

```
python -m venv venv
```

Activate:

* Windows:

```
venv\Scripts\activate
```

* Linux/Mac:

```
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install streamlit openai tiktoken PyPDF2 dotenv
```

### 4. Configure Environment Variables

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key
```

---

## Running the Application

```
streamlit run app.py
```

The application will launch locally in the browser.

---

## Error Handling and Edge Cases

The system accounts for:

* Empty or invalid input
* Poorly structured resumes
* Missing skill information
* Invalid GitHub links
* LLM response failures

Fallback strategies ensure that the pipeline continues to return usable structured outputs even under failure conditions.

---

## Design Decisions

### Use of Role Data

Predefined role skill sets are used to:

* Anchor gap analysis
* Avoid hallucinated requirements
* Maintain consistency across runs

### Agent-Based Architecture

Separating concerns into agents:

* Improves debuggability
* Enables targeted prompt optimization
* Allows independent scaling or replacement

### Streamlit Interface

Chosen for:

* Rapid prototyping
* Clear visualization of intermediate outputs
* Ease of demonstration

---
## Fallback and Reliability Mechanisms

To ensure robustness in real-world scenarios, the system implements structured fallback strategies across all agent stages. These mechanisms prevent pipeline failure and guarantee usable outputs even when LLM responses are incomplete, malformed, or unavailable.

### 1. Failure Scenarios Handled

The system detects and handles the following conditions:

* Empty or null LLM responses
* Invalid JSON outputs (parsing failures)
* Missing required keys (e.g., `skills`, `projects`)
* Inconsistent or hallucinated structure
* Upstream data sparsity (e.g., minimal resume content)

---

### 2. Fallback Strategy by Component

#### Profile Extraction Agent

If extraction fails or returns invalid structure:

* Returns a default schema:

```json
{
  "skills": {
    "core": [],
    "languages": [],
    "frameworks": [],
    "tools": [],
    "concepts": []
  },
  "projects": []
}
```

* Ensures downstream agents receive valid input format

---

#### Gap Identification Agent

If skill comparison fails:

* Uses role data directly to infer missing skills
* Assumes user has no matching skills when extraction is unreliable
* Prevents silent failure in gap analysis

---

#### Roadmap Generation Agent

If roadmap generation fails:

* Falls back to:

  * Predefined templates from `roadmaps.json`
  * Generic learning sequence based on role
* Ensures actionable output is always produced

---

#### Mock Interview Agent

If question generation fails:

* Uses static question bank (`interview_questions.json`)
* Filters questions based on role keywords

---

### 3. JSON Validation Layer

Each agent enforces:

* Schema validation
* Key presence checks
* Type consistency

Invalid outputs are automatically replaced with fallback structures before propagating forward.

---

### 4. Design Rationale

These fallback mechanisms ensure:

* Continuity: The pipeline never breaks mid-execution
* Predictability: Outputs always follow a known schema
* Resilience: System remains usable under LLM uncertainty
* Demo Reliability: Eliminates risk of failure during live demonstrations

---

### 5. Trade-offs

* Fallback outputs may be less personalized
* Over-reliance on defaults can reduce insight quality
* However, reliability is prioritized over completeness in failure scenarios


## Limitations

* Skill extraction depends on input quality
* Role definitions are static and may not reflect evolving industry trends
* Roadmaps are generated heuristically and may require human validation for production use

---

## Future Work
*Added 10 roles but skill extraction works on the first 6 need to update synthetic data for the last 4
* Normalization of ml -> machine learning,  c++ -> cpp, etc
* Dynamic role data via job scraping APIs
* Skill proficiency scoring
* Resume ranking and benchmarking
* Integration with real job descriptions
* Adaptive learning timelines based on user progress
* Deployment as an API service

---

## AI Disclosure

- Used AI tools: Yes (ChatGPT, OpenAI API)
- Verification:
  - Manually validated JSON outputs
  - Added schema checks and fallbacks
- Example rejected suggestion:
  - Initial extraction returned inconsistent skill categories, replaced with fixed schema enforcement



Skill Bridge Career Navigator demonstrates how LLM-based systems can be structured into reliable, modular pipelines that convert unstructured data into actionable insights. It bridges the gap between resume analysis and career planning by providing concrete, personalized next steps.
