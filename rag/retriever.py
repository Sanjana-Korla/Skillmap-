import numpy as np 
from rag.vector_store import VectorStoreManager 
from rag.loader import JobDescriptionLoader 

class CareerRAGRetriever: 
    def __init__(self): 
        self.vector_store_manager = VectorStoreManager() 
        self.db = self.vector_store_manager.build_or_load_index() 
        self.loader = JobDescriptionLoader() 
        
    def retrieve_context(self, query_role: str) -> dict: 
        query_clean = query_role.strip().lower() 
        all_docs = self.loader.load_all_jds() 
        unique_docs = [] 
        seen_doc_roles = set() 
        for doc in all_docs: 
            role_name = doc.metadata.get("role", "").strip().lower() 
            if role_name not in seen_doc_roles: 
                seen_doc_roles.add(role_name) 
                unique_docs.append(doc) 
        matched_doc = None 
        confidence_score = 0.0 
        match_method = "No Match" 
        
        # 1. Direct match comparison 
        for doc in unique_docs: 
            if doc.metadata.get("role", "").lower().strip() == query_clean: 
                matched_doc = doc 
                confidence_score = 1.0 
                match_method = "Exact String Match" 
                break 
                
        # 2. Key matching fallback 
        if not matched_doc: 
            for doc in unique_docs: 
                if query_clean in doc.metadata.get("role", "").lower().strip(): 
                    matched_doc = doc 
                    confidence_score = 0.90 
                    match_method = "Sub-string Fallback Match" 
                    break 
                    
        # 3. FAISS semantic search fallback 
        if not matched_doc: 
            results_with_scores = self.db.similarity_search_with_relevance_scores(query_role, k=1) 
            valid_results = [res for res in results_with_scores if res[1] > 0.12] 
            if valid_results: 
                matched_doc, confidence_score = valid_results[0] 
                confidence_score = float(confidence_score) 
                match_method = f"FAISS Semantic Vector Match (Similarity Score: {confidence_score:.2f})" 
                
        retrieved_roles = [] 
        sources = set() 
        all_skills = [] 
        all_responsibilities = [] 
        
        if matched_doc: 
            meta = matched_doc.metadata 
            retrieved_roles.append({ 
                "role": meta.get("role"), 
                "domain": meta.get("domain"), 
                "skills": meta.get("skills", []), 
                "responsibilities": meta.get("responsibilities", []), 
                "relevance": confidence_score 
            }) 
            sources.add(meta.get("source", "Unknown")) 
            all_skills.extend(meta.get("skills", [])) 
            all_responsibilities.extend(meta.get("responsibilities", [])) 
            
        explanation = ( 
            f"Retrieved target career profile via '{match_method}'. " 
            f"Factual grounding sourced from local database file '{list(sources)[0] if sources else 'N/A'}'. " 
            f"Parsed and verified {len(all_skills)} core target skillsets." 
        ) 
        
        return { 
            "retrieved_roles": retrieved_roles, 
            "confidence_score": confidence_score, 
            "source_count": len(sources), 
            "sources": list(sources), 
            "pooled_skills": list(set(all_skills)), 
            "pooled_responsibilities": list(set(all_responsibilities)), 
            "rag_explanation": explanation 
        }