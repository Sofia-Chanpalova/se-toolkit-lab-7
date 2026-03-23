"""LLM tool definitions for LMS backend endpoints."""

import json
from typing import Dict, Any, List
import httpx
from config import config

class LMSClient:
    """Client for LMS backend API."""
    
    def __init__(self):
        self.base_url = config.LMS_API_BASE_URL
        self.headers = {"Authorization": f"Bearer {config.LMS_API_KEY}"}
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make GET request to LMS backend."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self.headers
            )
            return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}

lms = LMSClient()

# Tool definitions for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks available in the system. Returns labs with titles and their associated tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of all enrolled students with their group information. Returns student IDs and group names.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution for a specific lab. Returns counts for 4 score buckets: 0-25, 26-50, 51-75, 76-100.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-02', etc."
                    }
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task pass rates and attempt counts for a specific lab. Shows performance for each task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-02', etc."
                    }
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline for a lab. Shows number of submissions per day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-02', etc."
                    }
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get group performance data for a lab. Shows average scores and student counts per group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-02', etc."
                    }
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top performing students for a lab. Returns list with scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-02', etc."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate for a lab. Returns percentage of students who completed all tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-02', etc."
                    }
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to update or refresh data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Tool implementations
async def execute_tool(tool_name: str, arguments: Dict) -> Any:
    """Execute a tool and return the result."""
    print(f"[tool] LLM called: {tool_name}({arguments})", file=sys.stderr)
    
    try:
        if tool_name == "get_items":
            result = await lms.get("/items/")
        elif tool_name == "get_learners":
            result = await lms.get("/learners/")
        elif tool_name == "get_scores":
            result = await lms.get(f"/analytics/scores", params={"lab": arguments["lab"]})
        elif tool_name == "get_pass_rates":
            result = await lms.get(f"/analytics/pass-rates", params={"lab": arguments["lab"]})
        elif tool_name == "get_timeline":
            result = await lms.get(f"/analytics/timeline", params={"lab": arguments["lab"]})
        elif tool_name == "get_groups":
            result = await lms.get(f"/analytics/groups", params={"lab": arguments["lab"]})
        elif tool_name == "get_top_learners":
            limit = arguments.get("limit", 5)
            result = await lms.get(f"/analytics/top-learners", params={"lab": arguments["lab"], "limit": limit})
        elif tool_name == "get_completion_rate":
            result = await lms.get(f"/analytics/completion-rate", params={"lab": arguments["lab"]})
        elif tool_name == "trigger_sync":
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{lms.base_url}/pipeline/sync",
                    headers=lms.headers
                )
                result = resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        print(f"[tool] Result: {str(result)[:200]}...", file=sys.stderr)
        return result
    except Exception as e:
        print(f"[tool] Error: {e}", file=sys.stderr)
        return {"error": str(e)}

# Импортируем sys для stderr
import sys
