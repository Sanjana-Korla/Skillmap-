from utils.gemini_helper import GeminiHelper 
class RoadmapBuilderAgent: 
    def __init__(self): 
        self.helper = GeminiHelper() 

    def build_roadmap(self, target_role: str, gap_report: dict, resources_data: dict, duration_weeks: int = 8) -> dict: 
        missing_skills = [m["skill"] for m in gap_report.get("missing_skills", [])] 
        weak_skills = [w["skill"] for w in gap_report.get("weak_skills", [])] 
        system_prompt = """ 
        You are an elite Tech Career Coach & Curriculum Designer. 
        Construct a highly concise week-by-week curriculum based on the provided target role and skill gaps. 
        Prioritize skills with the highest demand scores first. 
        You MUST integrate the provided curated learning resources directly into the weeks they belong. Use the actual resource titles and URLs provided in the resources context. 
        """ 
        user_prompt = f""" 
        Target Role: {target_role} 
        Total Weeks Plan duration: {duration_weeks} Weeks 
        Missing High Priority Skills to acquire: {missing_skills} 
        Weak Skills to polish: {weak_skills} 
        Available Curated Resources Context (Mapped by Skill): 
        {resources_data} 
        CRITICAL PERFORMANCE RULES FOR SPEED: 
        - Keep 'curriculum_goal' and 'expected_outcome' extremely short and concise (under 10 words). 
        - Keep 'topics' list to exactly 2 short items. 
        - Minimize output tokens to ensure rapid API generation. 
        CRITICAL RULES FOR WEEK-BY-WEEK GENERATION: 
        1. Ensure every week has a unique, progressive skill title in 'focus_skills'. 
        2. NEVER repeat the exact same skill title across multiple weeks. 
        3. If a complex skill takes multiple weeks to learn, append a progressive suffix (e.g. "SQL Basics", "SQL Advanced"). 
        4. Every week's "resources" list MUST contain EXACTLY 2 resources. Use matching items from the Available Curated Resources Context. 
           If the context only contains 1 curated resource for that specific technology skill, you MUST synthesize a highly realistic, high-quality secondary learning resource from standard reputable platforms (such as Coursera, Udemy, or YouTube) matching the target technology, so that every week has EXACTLY 2 resources. Do not leave the resources list empty or under 2 items.
        Return a structured JSON payload matching this exact layout: 
        {{ 
          "roadmap_title": "Custom Career Acceleration Roadmap", 
          "weeks": [ 
            {{ 
              "week_number": 1, 
              "focus_skills": ["Unique Progressive Skill Name"], 
              "topics": ["Concrete Topic 1", "Concrete Topic 2"], 
              "estimated_hours": 10, 
              "curriculum_goal": "Short goal under 10 words.", 
              "expected_outcome": "Short outcome under 10 words.", 
              "resources": [ 
                {{ 
                  "title": "Exact Title of the Resource 1", 
                  "platform": "YouTube / Coursera / NPTEL", 
                  "url": "Exact URL 1" 
                }},
                {{ 
                  "title": "Title of the Supplementary Resource 2", 
                  "platform": "YouTube / Coursera / NPTEL", 
                  "url": "URL 2" 
                }} 
              ] 
            }} 
          ] 
        }} 
        Ensure total weeks mapped matches exactly {duration_weeks}. 
        """ 
        result = self.helper.generate_json(system_prompt, user_prompt) 
        return result