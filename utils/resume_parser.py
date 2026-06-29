import re 
from pypdf import PdfReader 

class SimpleResumeParser: 
    def __init__(self): 
        # Expanded database mapping all distinct skills represented in your target role JSONs 
        self.common_skills_db = [ 
            # Core Languages & Fundamentals 
            "python", "javascript", "sql", "java", "c++", "php", "typescript", "html", "css", 
            "data structures", "algorithms", "object-oriented programming", "oop", "mathematics", "statistics", 
            # AI / ML / Deep Learning 
            "machine learning", "deep learning", "neural networks", "computer vision", "opencv", 
            "nlp", "transformers", "hugging face", "llms", "prompt engineering", "langchain", 
            "rag", "vector databases", "pytorch", "tensorflow", "cnns", "model optimization", 
            "gpu computing", "generative ai", "prompt optimization", "recommendation systems", 
            "collaborative filtering", "reinforcement learning", "simulation", "robotics", "ros", 
            "sensor fusion", "control systems", "model evaluation", "fine-tuning", 
            "text processing", "image processing", "api development", "api integration",
            # Data Science & Analytics 
            "data analysis", "data visualization", "feature engineering", "excel", "power bi", 
            "tableau", "data cleaning", "business intelligence", "requirements analysis", "excel vba", 
            "data warehousing", "hadoop", "data pipelines", "apache spark", "etl", "snowflake", 
            "financial modeling", "monte carlo simulation", "hypothesis testing", "pandas", "numpy", 
            "a/b testing", "dashboard design", "dax", "sas", "google analytics", "product analytics", 
            "data modeling", "data mining", "process optimization",
            # Web Development & Software Engineering 
            "responsive design", "bootstrap", "web performance", "node.js", "rest apis", "mongodb", 
            "express.js", "redux", "angular", "rxjs", "figma", "adobe xd", "ui design", "ux design", 
            "wireframing", "prototyping", "wordpress", "mysql", "theme development", "plugin development", 
            "django", "flask", "spring boot", "hibernate", "microservices", "testing", "debugging", "postman", 
            "database design", "web application development",
            # Cloud, MLOps, DevOps & Systems 
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "linux", "terraform", 
            "prometheus", "grafana", "networking", "shell scripting", "ansible", "monitoring", 
            "api security", "system design", "mlops", "ci/cd", "model deployment", "git" 
        ] 
        
    def extract_skills_from_text(self, text: str) -> list[str]: 
        text_lower = text.lower() 
        extracted = [] 
        for skill in self.common_skills_db: 
            # Matches complete word phrases to avoid partial matches 
            pattern = r'\b' + re.escape(skill) + r'\b' 
            if re.search(pattern, text_lower): 
                extracted.append(skill.title()) 
        return list(set(extracted)) 
        
    def parse_pdf(self, file_bytes) -> list[str]: 
        try: 
            reader = PdfReader(file_bytes) 
            text = "" 
            for page in reader.pages: 
                text += page.extract_text() or "" 
            return self.extract_skills_from_text(text) 
        except Exception: 
            return []