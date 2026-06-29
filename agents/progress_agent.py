class ProgressTrackerAgent: 
    def __init__(self): 
        pass 
        
    def calculate_progress(self, completed_weeks: list[int], total_weeks: int) -> float: 
        if total_weeks == 0: 
            return 0.0 
        pct = (len(completed_weeks) / total_weeks) * 100 
        return round(pct, 1) 
        
    def recalculate_roadmap_gaps(self, original_gaps: dict, completed_skills: list[str]) -> dict: 
        updated_missing = [ 
            m for m in original_gaps.get("missing_skills", []) 
            if m["skill"].lower() not in [cs.lower() for cs in completed_skills] 
        ] 
        updated_weak = [ 
            w for w in original_gaps.get("weak_skills", []) 
            if w["skill"].lower() not in [cs.lower() for cs in completed_skills] 
        ] 
        original_match = original_gaps.get("match_score", 0) 
        total_gaps = len(original_gaps.get("missing_skills", [])) + len(original_gaps.get("weak_skills", [])) 
        
        if total_gaps == 0: 
            new_match = 100.0 
        else: 
            leftover_gaps = len(updated_missing) + len(updated_weak) 
            repaired = total_gaps - leftover_gaps 
            new_match = min(100.0, original_match + (repaired / total_gaps) * (100.0 - original_match)) 
            
        return { 
            "match_score": round(new_match, 1), 
            "missing_skills": updated_missing, 
            "weak_skills": updated_weak, 
            "matched_skills": original_gaps.get("matched_skills", []) + [{"skill": s} for s in completed_skills] 
        }