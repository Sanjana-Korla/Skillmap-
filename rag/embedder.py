from langchain_huggingface import HuggingFaceEmbeddings 

class Embedder: 
    def __init__(self): 
        # Local model implementation for embedding generation 
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
        
    def get_model(self): 
        return self.embedding_model