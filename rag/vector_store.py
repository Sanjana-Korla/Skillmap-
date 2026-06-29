import os 
from langchain_community.vectorstores import FAISS 
from rag.loader import JobDescriptionLoader 
from rag.embedder import Embedder 

class VectorStoreManager: 
    def __init__(self, index_path: str = "faiss_index"): 
        self.index_path = index_path 
        self.loader = JobDescriptionLoader() 
        self.embedder = Embedder() 
        
    def build_or_load_index(self, force_rebuild: bool = False) -> FAISS: 
        if not force_rebuild and os.path.exists(self.index_path): 
            embeddings = self.embedder.get_model() 
            return FAISS.load_local(self.index_path, embeddings, allow_dangerous_deserialization=True) 
        else: 
            documents = self.loader.load_all_jds() 
            if not documents: 
                from langchain_core.documents import Document 
                documents = [Document(page_content="Placeholder role", metadata={"role": "None", "domain": "None", "skills": [], "responsibilities": []})] 
            embeddings = self.embedder.get_model() 
            db = FAISS.from_documents(documents, embeddings) 
            db.save_local(self.index_path) 
            return db