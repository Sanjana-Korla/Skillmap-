import json 
from langchain_core.tools import tool 

class GapIdentifierAgent: 
    def __init__(self): 
        pass 
    
    def identify_gaps(self, user_skills: list[str], market_demand: dict, proficiency_levels: dict) -> dict: 
        demand_scores = market_demand.get("demand_scores", {}) 
        matched_skills = [] 
        missing_skills = [] 
        weak_skills = [] 
        user_skills_clean = [s.strip().lower() for s in user_skills] 
        user_proficiency_clean = {k.strip().lower(): v.strip().lower() for k, v in proficiency_levels.items()} 
        
        # Dialect Mapping: If a developer knows a specific SQL dialect, they know standard SQL
        if any(db in user_skills_clean for db in ["mysql", "postgresql", "sqlite", "oracle", "sql server"]):
            if "sql" not in user_skills_clean:
                user_skills_clean.append("sql")
        
        for market_skill, demand in demand_scores.items(): 
            market_skill_lower = market_skill.lower() 
            if market_skill_lower in user_skills_clean: 
                prof = user_proficiency_clean.get(market_skill_lower, "intermediate") 
                if prof == "beginner": 
                    weak_skills.append({ 
                        "skill": market_skill, 
                        "demand": demand, 
                        "gap_severity": 0.5, 
                        "priority_score": round(0.5 * demand, 2) 
                    }) 
                else: 
                    matched_skills.append({ 
                        "skill": market_skill, 
                        "demand": demand 
                    }) 
            else: 
                missing_skills.append({ 
                    "skill": market_skill, 
                    "demand": demand, 
                    "gap_severity": 1.0, 
                    "priority_score": round(1.0 * demand, 2) 
                }) 
        
        missing_skills.sort(key=lambda x: x["priority_score"], reverse=True) 
        weak_skills.sort(key=lambda x: x["priority_score"], reverse=True) 
        required_count = len(demand_scores) 
        matched_count = len(matched_skills) 
        match_score = round((matched_count / required_count) * 100, 1) if required_count > 0 else 100.0 
        
        return { 
            "match_score": match_score, 
            "matched_skills": matched_skills, 
            "missing_skills": missing_skills, 
            "weak_skills": weak_skills 
        } 

@tool 
def compute_priority_gaps_tool(user_skills_json: str, market_skills_json: str) -> str: 
    """ 
    Cross-references raw skills data to list missing or weak domain gaps. 
    """ 
    try: 
        agent = GapIdentifierAgent()
        u_skills = json.loads(user_skills_json) 
        m_demand = {"demand_scores": {k: 1.0 for k in json.loads(market_skills_json)}} 
        return json.dumps(agent.identify_gaps(u_skills, m_demand, {})) 
    except Exception as e: 
        return f"Parsing Error: {str(e)}"