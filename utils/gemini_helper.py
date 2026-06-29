import os 
import json 
import time 
import streamlit as st 
from dotenv import load_dotenv 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import SystemMessage, HumanMessage 

load_dotenv() 

class GeminiHelper: 
    def __init__(self): 
        api_key = os.getenv("GOOGLE_API_KEY") 
        if not api_key: 
            try: 
                api_key = st.secrets["GOOGLE_API_KEY"] 
                os.environ["GOOGLE_API_KEY"] = api_key 
            except Exception: 
                raise ValueError("GOOGLE_API_KEY not found. Please set it in your environment, .env file, or Streamlit Secrets.") 
        self.llm = ChatGoogleGenerativeAI( 
            model="gemini-2.5-flash", 
            temperature=0.2, 
            google_api_key=api_key, 
            model_kwargs={"response_format": {"type": "json_object"}} 
        ) 

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict: 
        """Helper to ensure Structured JSON is returned with rate-limit retry support.""" 
        messages = [ 
            SystemMessage(content=system_prompt + "\nReturn ONLY structured JSON. Do not include markdown code block formatting like ```json or any other text."), 
            HumanMessage(content=user_prompt) 
        ] 
        max_retries = 3 
        backoff_delay = 2 # Seconds to wait before retrying 
        for attempt in range(max_retries): 
            try: 
                response = self.llm.invoke(messages) 
                text = response.content.strip() 
                if text.startswith("```"): 
                    text = text.split("\n", 1)[1] 
                if text.endswith("```"): 
                    text = text.rsplit("\n", 1)[0] 
                text = text.strip() 
                return json.loads(text) 
            except Exception as e: 
                # Check for rate-limiting (Resource Exhausted / 429) 
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e): 
                    if attempt < max_retries - 1: 
                        time.sleep(backoff_delay * (attempt + 1)) # Exponential backoff 
                        continue 
                return {"error": f"Failed to generate structured JSON: {str(e)}", "raw": ""}

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Helper to generate plain text/markdown directly to prevent JSON parsing errors on long reports."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        max_retries = 3
        backoff_delay = 2
        api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
        
        # Use a standard text-based configuration without json response constraints
        text_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=api_key
        )
        for attempt in range(max_retries):
            try:
                response = text_llm.invoke(messages)
                return response.content.strip()
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(backoff_delay * (attempt + 1))
                        continue
                return f"Failed to generate evaluation due to API error: {str(e)}"