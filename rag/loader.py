import os 
import json 
from langchain_core.documents import Document 

class JobDescriptionLoader: 
    def __init__(self, data_dir: str = "data"): 
        self.data_dir = data_dir 
        
    def load_all_jds(self) -> list[Document]: 
        documents = [] 
        if not os.path.exists(self.data_dir): 
            os.makedirs(self.data_dir) 
        for file_name in os.listdir(self.data_dir): 
            # Isolates Job Profiles index from course library data 
            if file_name.endswith(".json") and file_name != "resources.json": 
                file_path = os.path.join(self.data_dir, file_name) 
                try: 
                    with open(file_path, 'r', encoding='utf-8') as f: 
                        data = json.load(f) 
                    if isinstance(data, dict): 
                        data = [data] 
                    for entry in data: 
                        role = entry.get("role", "Unknown Role") 
                        domain = entry.get("domain", "Unknown Domain") 
                        skills = entry.get("skills", []) 
                        responsibilities = entry.get("responsibilities", []) 
                        content = ( 
                            f"Role: {role}\n" 
                            f"Domain: {domain}\n" 
                            f"Required Skills: {', '.join(skills)}\n" 
                            f"Key Responsibilities: {', '.join(responsibilities)}" 
                        ) 
                        metadata = { 
                            "source": file_name, 
                            "role": role, 
                            "domain": domain, 
                            "skills": skills, 
                            "responsibilities": responsibilities 
                        } 
                        documents.append(Document(page_content=content, metadata=metadata)) 
                except Exception as e: 
                    print(f"Error loading file {file_name}: {str(e)}") 
        return documents