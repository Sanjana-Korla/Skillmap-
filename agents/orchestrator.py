import os
import ast
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from agents.skill_profiler import profile_user_tool
from agents.market_agent import analyze_market_skills_tool
from agents.gap_agent import compute_priority_gaps_tool

class CareerAgentOrchestrator:
    def __init__(self):
        # 1. Instantiate an unrestricted LLM instance for tool-calling execution
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=api_key
        )
        
        self.tools = [profile_user_tool, analyze_market_skills_tool, compute_priority_gaps_tool]
        
        # 2. Arrange prompt in strict sequence: System -> Human -> Agent Scratchpad
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an elite career planning intelligence system. 
            You possess active reasoning tools to normalize user developer skills, retrieve market benchmarks, and compute gaps.
            Answer user questions step-by-step using your tools to ensure structural accuracy.
            """),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

    def _clean_output(self, output) -> str:
        """Robust parser to extract clean human-readable text from raw API message blocks."""
        if not output:
            return "Could not formulate an evaluation."
        
        # Handle string representations of lists/dicts
        if isinstance(output, str):
            output_strip = output.strip()
            if output_strip.startswith("[") and output_strip.endswith("]"):
                try:
                    parsed = ast.literal_eval(output_strip)
                    if isinstance(parsed, (list, dict)):
                        output = parsed
                except Exception:
                    pass
            elif output_strip.startswith("{") and output_strip.endswith("}"):
                try:
                    parsed = ast.literal_eval(output_strip)
                    if isinstance(parsed, dict):
                        output = parsed
                except Exception:
                    pass

        # Handle list of items (extract only the text value from blocks)
        if isinstance(output, list):
            extracted_texts = []
            for item in output:
                if isinstance(item, str):
                    extracted_texts.append(item.strip())
                else:
                    text_val = ""
                    try:
                        if isinstance(item, dict):
                            text_val = item.get("text") or item.get("content") or ""
                        else:
                            # Try object attribute lookups on custom LangChain classes
                            text_val = getattr(item, "text", None) or getattr(item, "content", None)
                            if not text_val:
                                # Try dictionary subscriptions
                                try:
                                    text_val = item["text"]
                                except Exception:
                                    try:
                                        text_val = item["content"]
                                    except Exception:
                                        pass
                    except Exception:
                        pass
                    
                    # Regex Fallback: parse raw output representation for 'text' block if standard lookups fail
                    if not text_val:
                        item_str = str(item)
                        match = re.search(r"['\"]text['\"]\s*:\s*['\"](.*?)['\"](?=,\s*['\"]|\s*})", item_str, re.DOTALL)
                        if match:
                            text_val = match.group(1)
                        else:
                            if "extras" not in item_str and "signature" not in item_str:
                                text_val = item_str
                                
                    if text_val:
                        extracted_texts.append(str(text_val).strip())
            return " ".join([t for t in extracted_texts if t])
            
        # Handle single dictionaries
        if isinstance(output, dict):
            return str(output.get("text") or output.get("content") or output)
            
        return str(output)
        
    def query(self, user_message: str) -> str:
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        response = executor.invoke({"input": user_message})
        output = response.get("output")
        return self._clean_output(output)