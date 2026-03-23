"""LLM-powered intent router for natural language queries."""

import json
import sys
import httpx
from typing import List, Dict, Any
from config import config
from tools import TOOLS, execute_tool

SYSTEM_PROMPT = """You are an LMS assistant bot. Your job is to help users get information about labs, scores, and student performance.

You have access to tools that can fetch data from the LMS backend. Use these tools to answer user questions.

When a user asks a question:
1. Decide what information they need
2. Call the appropriate tool(s) to get that data
3. Use the results to formulate a helpful, concise answer

For questions about lab performance, you may need to call get_items first to see what labs exist, then call get_pass_rates for each lab to compare.

Be friendly and helpful. If you can't answer a question, politely explain what you can help with.

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Get score distribution for a lab
- get_pass_rates: Get per-task pass rates for a lab
- get_timeline: Get submission timeline for a lab
- get_groups: Get group performance for a lab
- get_top_learners: Get top performing students
- get_completion_rate: Get completion rate for a lab
- trigger_sync: Refresh data from autochecker"""

class LLMRouter:
    def __init__(self):
        self.base_url = config.LLM_API_BASE_URL
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_API_MODEL
        
    async def chat(self, messages: List[Dict]) -> Dict:
        """Send chat completion request to LLM."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice": "auto",
                    "max_tokens": 1000
                }
            )
            return resp.json()
    
    async def route(self, user_message: str) -> str:
        """Route user message to appropriate tool and return response."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        print(f"[router] Processing: {user_message}", file=sys.stderr)
        
        # Continue until no more tool calls
        while True:
            response = await self.chat(messages)
            
            if "error" in response:
                error_msg = response.get("error", {}).get("message", "Unknown error")
                print(f"[router] LLM error: {error_msg}", file=sys.stderr)
                return f"❌ LLM error: {error_msg}"
            
            message = response["choices"][0]["message"]
            
            # Check if there are tool calls
            if message.get("tool_calls"):
                # Execute all tool calls
                tool_results = []
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    result = await execute_tool(tool_name, arguments)
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                # Add assistant message and tool results to conversation
                messages.append(message)
                messages.extend(tool_results)
                print(f"[router] Executed {len(tool_results)} tools, continuing...", file=sys.stderr)
                continue
            
            # No tool calls, return the response
            content = message.get("content", "")
            print(f"[router] Final response: {content[:100]}...", file=sys.stderr)
            return content
        
        return "Sorry, I couldn't process that request."

# Create global router instance
router = LLMRouter()
