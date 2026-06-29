# SkillMap - Agentic Career Intelligence System

SkillMap is an agentic talent intelligence system designed to analyze a candidate's current developer skills, map them against factual job description benchmarks retrieved via RAG, identify high-priority gaps, and build a tailored week-by-week upskilling roadmap with verified learning resources.

This system is built specifically to solve the problem of students and transitioning professionals who finish bootcamps or courses but struggle to identify, prioritize, and structure their next learning steps.

---

## Multi-Agent Architecture

SkillMap coordinates four distinct cooperative agents to construct the overall evaluation pipeline:

1. **Skill Profiler Agent** (`agents/skill_profiler.py`):
   - **Role**: Standardizes raw user inputs (or text extracted from uploaded resume PDFs) against the reference industry taxonomy to group, score, and evaluate taxonomic overlap.
   - **Real Tools**: `profile_user_tool` (validates custom developer inputs, handles dialect normalizations, and calculates baseline competence metrics).

2. **Market Demand Agent** (`agents/market_agent.py`):
   - **Role**: Queries the vector-backed local job description database to retrieve contextual benchmarks and compute co-occurrence frequencies.
   - **Real Tools**: `analyze_market_skills_tool` (executes RAG queries and parses co-occurrences).

3. **Gap Identifier Agent** (`agents/gap_agent.py`):
   - **Role**: Formulates a quantitative comparison between the user's profile and target benchmarks, sorting gap severity and calculating an ROI/urgency score.
   - **Real Tools**: `compute_priority_gaps_tool`.

4. **Roadmap Builder Agent** (`agents/roadmap_agent.py`):
   - **Role**: Interacts with the `ResourceRecommendationAgent` to dynamically retrieve resources and designs a structured week-by-week curriculum.

---

## Key Features

1. **PDF Resume Parser**: Bootstrap profiles directly using PyPDF semantic text extraction.
2. **Ground Truth RAG Verification**: Real job profiles are indexed in FAISS using Hugging Face embeddings (all-MiniLM-L6-v2) to eliminate hallucination.
3. **Dynamic Gap Visualizations**: Matplotlib-powered horizontal frequency distributions and side-by-side benchmark bar charts.
4. **Dynamic Progress Recalculation**: Progress Hub allows users to check off weekly milestones, triggering immediate updates to their match rating.
5. **AI Advisor Assistant**: An autonomous chatbot powered by a LangChain AgentExecutor that handles technical questions step-by-step.
6. **PDF Export Utility**: Compiles and generates a tailored career track blueprint using ReportLab.

---

## Tech Stack

1. **LLM Model**: Gemini 2.5 Flash (gemini-2.5-flash)
2. **Frameworks**: LangChain, LangChain-Core, LangChain-Community, LangChain-HuggingFace
3. **Vector Database**: FAISS (Facebook AI Similarity Search)
4. **Embedding Model**: Hugging Face (all-MiniLM-L6-v2)
5. **Parsing & Rendering**: PyPDF, Matplotlib, ReportLab
6. **Frontend UI**: Streamlit
