import json 
import os 
from utils.gemini_helper import GeminiHelper 
from langchain_core.tools import tool 

class SkillProfilerAgent: 
    def __init__(self, data_dir: str = "data"): 
        self.helper = GeminiHelper() 
        self.data_dir = data_dir 
        self.taxonomy_skills = self._load_taxonomy_skills() 

    def _load_taxonomy_skills(self) -> list[str]: 
        """Builds a flat skill taxonomy from the local job descriptions JSONs.""" 
        skills = set() 
        if os.path.exists(self.data_dir): 
            for file_name in os.listdir(self.data_dir): 
                if file_name.endswith(".json") and file_name != "resources.json": 
                    try: 
                        with open(os.path.join(self.data_dir, file_name), "r", encoding="utf-8") as f: 
                            data = json.load(f) 
                            for entry in data: 
                                for s in entry.get("skills", []): 
                                    skills.add(s.strip()) 
                    except Exception: 
                        pass 
        return sorted(list(skills)) 

    def profile_user(self, raw_skills: list[str], proficiency_levels: dict, experience_years: float) -> dict: 
        skills_str = ", ".join(raw_skills) 
        levels_str = ", ".join([f"{k}: {v}" for k, v in proficiency_levels.items()]) 
        taxonomy_str = ", ".join(self.taxonomy_skills[:100]) # Feed reference taxonomy to avoid token overflow 
        system_prompt = f""" 
        You are an expert Talent Intelligence profiling system. 
        Your goal is to analyze raw developer skill inputs, validate them against the provided reference industry taxonomy, and output a structured profile. 
        Reference Taxonomy: 
        [{taxonomy_str}] 
        """ 
        user_prompt = f""" 
        User Raw Skills: {skills_str} 
        Proficiency Map: {levels_str} 
        Years of Experience: {experience_years} 
        Compare the raw inputs with the Reference Taxonomy. Resolve matching synonyms, use standardized conventions, and categorize them. 
        Return a JSON structure matching exactly: 
        {{ 
        "normalized_skills": ["NormalizedSkill1", "NormalizedSkill2"], 
        "skill_groups": {{ 
        "CategoryName": ["Skill1", "Skill2"] 
        }}, 
        "profile_score": 0.0 to 100.0, 
        "confidence_assessment": "High/Medium/Low based on details provided", 
        "taxonomy_overlap_percentage": 0.0 
        }} 
        """ 
        result = self.helper.generate_json(system_prompt, user_prompt) 

        
        # SAFEGUARD 1: Ensure normalized_skills field is populated
        
        if "normalized_skills" not in result or not isinstance(result["normalized_skills"], list): 
            result["normalized_skills"] = list(set([s.strip().title() for s in raw_skills])) 

        
        # SAFEGUARD 2: Restore any skills omitted by the LLM (e.g. restoring SQL)
        
        norm_skills_lower = [s.lower() for s in result["normalized_skills"]]
        raw_skills_clean = [s.strip() for s in raw_skills if s.strip()]
        
        for raw in raw_skills_clean:
            if raw.lower() not in norm_skills_lower:
                normalized_name = "SQL" if raw.lower() == "sql" else raw.title()
                result["normalized_skills"].append(normalized_name)

        
        # SAFEGUARD 3: Prevent empty skill_groups or unmapped skills
        
        if "skill_groups" not in result or not isinstance(result["skill_groups"], dict):
            result["skill_groups"] = {}

        # Track which skills are already represented in categorizations
        all_grouped_skills = []
        for group, g_skills in result["skill_groups"].items():
            if isinstance(g_skills, list):
                all_grouped_skills.extend([s.lower() for s in g_skills])

        # If the LLM omitted SQL from all groups, automatically place it under "Other Technical Skills"
        for skill in result["normalized_skills"]:
            if skill.lower() not in all_grouped_skills:
                if "Other Technical Skills" not in result["skill_groups"]:
                    result["skill_groups"]["Other Technical Skills"] = []
                result["skill_groups"]["Other Technical Skills"].append(skill)

        # Deduplicate skills inside the same group if any duplicates exist
        for group in list(result["skill_groups"].keys()):
            group_list = result["skill_groups"][group]
            if isinstance(group_list, list):
                seen = set()
                unique_group = []
                for s in group_list:
                    s_lower = s.lower()
                    if s_lower not in seen:
                        seen.add(s_lower)
                        unique_group.append(s)
                result["skill_groups"][group] = unique_group

        
        # SAFEGUARD 4: Fallback calculations for baseline safety metrics
        
        if "profile_score" not in result:
            result["profile_score"] = min(100.0, float(len(raw_skills) * 8 + experience_years * 5)) 
        if "confidence_assessment" not in result:
            result["confidence_assessment"] = "High" if len(raw_skills) > 2 else "Medium"
        if "taxonomy_overlap_percentage" not in result:
            result["taxonomy_overlap_percentage"] = 50.0 

        return result 

@tool 
def profile_user_tool(skills_list: str) -> str: 
    """ 
    Helper tool to parse, normalize, and score raw developer profile inputs. 
    """ 
    raw_list = [s.strip() for s in skills_list.split(",") if s.strip()] 
    agent = SkillProfilerAgent() 
    result = agent.profile_user(raw_list, {}, 1.0) 
    return json.dumps(result)