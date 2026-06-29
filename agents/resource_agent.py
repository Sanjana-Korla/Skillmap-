import os 
import json 
from langchain_core.documents import Document 
from langchain_community.vectorstores import FAISS 
from rag.embedder import Embedder 

class ResourceRecommendationAgent: 
    def __init__(self, resources_path: str = "data/resources.json", index_path: str = "faiss_resources_index"): 
        self.resources_path = resources_path 
        self.index_path = index_path
        self.embedder = Embedder() 
        self.db = self._build_or_load_resource_index() 

    def _build_or_load_resource_index(self): 
        embeddings = self.embedder.get_model()
        
        # Check if index already exists locally to avoid redundant embedding generation
        if os.path.exists(self.index_path):
            return FAISS.load_local(self.index_path, embeddings, allow_dangerous_deserialization=True)
            
        documents = [] 
        if os.path.exists(self.resources_path): 
            try: 
                with open(self.resources_path, 'r', encoding='utf-8') as f: 
                    resources = json.load(f) 
                for item in resources: 
                    content = f"Skill: {item['skill']}\nTitle: {item['title']}\nPlatform: {item['platform']}" 
                    metadata = { 
                        "skill": item["skill"], 
                        "title": item["title"], 
                        "platform": item["platform"], 
                        "url": item["url"] 
                    } 
                    documents.append(Document(page_content=content, metadata=metadata)) 
            except Exception as e: 
                print(f"Error reading resources file: {str(e)}") 
                
        if not documents: 
            documents = [Document(page_content="Placeholder Resource", metadata={"skill": "None", "title": "None", "platform": "None", "url": ""})] 
            
        # Build and persist index
        db = FAISS.from_documents(documents, embeddings) 
        db.save_local(self.index_path)
        return db

    def recommend_resources(self, skills_list: list[str], k: int = 2) -> dict:
        """
        Retrieves relevant learning resources for a list of skills.
        Returns a dictionary mapping each skill to its recommended resources.
        """
        recommendations = {}
        for skill in skills_list:
            skill_clean = skill.strip().lower()
            matched_items = []
            
            # 1. Direct match check from local JSON to prioritize exact sources
            if os.path.exists(self.resources_path):
                try:
                    with open(self.resources_path, 'r', encoding='utf-8') as f:
                        resources_data = json.load(f)
                    for item in resources_data:
                        if item.get("skill", "").strip().lower() == skill_clean:
                            matched_items.append({
                                "title": item.get("title"),
                                "platform": item.get("platform"),
                                "url": item.get("url")
                            })
                except Exception as e:
                    print(f"Error reading local resources for direct match: {e}")
            
            # 2. Vector search query fallback to fill remaining resource spots
            if len(matched_items) < k and self.db:
                try:
                    # Query vector DB using standard format
                    results = self.db.similarity_search(f"Skill: {skill}", k=k)
                    for doc in results:
                        meta = doc.metadata
                        if meta.get("skill") != "None":
                            item = {
                                "title": meta.get("title"),
                                "platform": meta.get("platform"),
                                "url": meta.get("url")
                            }
                            if item not in matched_items:
                                matched_items.append(item)
                except Exception as e:
                    print(f"FAISS search fallback failed for skill '{skill}': {e}")
            
            # Assign recommendations up to limit 'k'
            if matched_items:
                recommendations[skill] = matched_items[:k]
                
        return recommendations