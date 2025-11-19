from typing import Any, Dict
import json
import re
import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from tools import get_job_info_tool, find_recruiter_candidates_tool

load_dotenv()


class RecruiterFinderAgent:
    
    DEFAULT_MODEL = "grok-beta"
    DEFAULT_BASE_URL = "https://api.x.ai/v1"
    
    SYSTEM_PROMPT = (
        "You are an assistant that finds recruiter or HR contact details for job postings.\n\n"
        "Your workflow:\n"
        "1. First, use get_job_info_tool with the job URL to extract: company_name, job_title, source, and job_url.\n"
        "2. Then, use find_recruiter_candidates_tool with the company_name (and optionally job_title) to find recruiter/HR contacts.\n"
        "3. Format the results as JSON with this exact structure:\n"
        "{\n"
        '  "company": "<company_name>",\n'
        '  "job_title": "<job_title>",\n'
        '  "source": "<source>",\n'
        '  "job_url": "<job_url>",\n'
        '  "recruiters": [\n'
        '    {"name": "<name>", "title": "<title>", "email": "<email>", "linkedin": "<linkedin_url>"}\n'
        '  ]\n'
        "}\n\n"
        "Important: Return ONLY valid JSON, no additional text or markdown formatting."
    )
    
    def __init__(
        self, 
        model_name: str = None,
        api_key: str = None,
        base_url: str = None,
    ):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        if not self.api_key:
            raise ValueError(
                "GROK_API_KEY is not set in environment. "
                "Please add it to your .env file."
            )
        
        self._agent = None
        self._build_agent()
    
    def _build_agent(self) -> None:

        tools = [get_job_info_tool, find_recruiter_candidates_tool]

        model = ChatOpenAI(
            model=self.model_name,
            temperature=0,
            api_key=self.api_key,
            base_url=self.base_url,
        )

        self._agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    def find_recruiters_for_job(self, job_url: str) -> Dict[str, Any]:

        user_instruction = (
            f"Find recruiter or HR contact emails for this job posting: {job_url}\n\n"
            "Please extract the job information and find recruiter contacts. "
            "Return the result as JSON only."
        )

        try:
            state = self._agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_instruction,
                        }
                    ]
                }
            )

            messages = state.get("messages", [])
            if not messages:
                raise RuntimeError("Agent returned no messages.")

            final_msg = messages[-1]
            content = getattr(final_msg, "content", None) or final_msg.get("content", "")
            
            if not content:
                raise ValueError("Agent returned empty content.")

            return self._parse_agent_response(content)
            
        except Exception as e:
            return {
                "error": "Agent execution failed",
                "error_message": str(e),
            }
    
    def _parse_agent_response(self, content: Any) -> Dict[str, Any]:
        content_str = str(content)

        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content_str, re.DOTALL)
        if json_match:
            content_str = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
            if json_match:
                content_str = json_match.group(0)

        # Parse JSON
        try:
            parsed = json.loads(content_str)
            return parsed
        except json.JSONDecodeError as e:
            # Fallback
            return {
                "error": "Failed to parse JSON from agent response",
                "parse_error": str(e),
                "raw_content": content_str[:500],
            }


# Backward compatibility functions
def build_agent(model_name: str = "grok-beta") -> Any:
    agent_finder = RecruiterFinderAgent(model_name=model_name)
    return agent_finder._agent


def find_recruiters_for_job(job_url: str, agent: Any) -> Dict[str, Any]:
    agent_finder = RecruiterFinderAgent()
    return agent_finder.find_recruiters_for_job(job_url)
