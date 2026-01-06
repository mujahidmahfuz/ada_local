"""
Centralized configuration for Pocket AI.
"""

# --- Model Configuration ---
RESPONDER_MODEL = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434/api"
LOCAL_ROUTER_PATH = "./merged_model"
MAX_HISTORY = 20

# --- TTS Configuration ---
TTS_VOICE_MODEL = "en_GB-alba-medium"
TTS_MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx"
TTS_CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json"

# --- Router Keywords ---
# Keywords that trigger the Router (otherwise we default to chat)
ROUTER_KEYWORDS = [
    # Tools
    "turn", "light", "dim", "switch",   # Lights
    "search", "google", "find", "look", # Search
    "timer", "alarm", "clock",          # Timers
    "calendar", "schedule", "appoint", "meet", "event", # Calendar
    
    # Complexity / Thinking Triggers (from Training Data)
    "explain", "how", "why", "cause", "difference", "compare", "meaning", # Reasoning
    "solve", "calculate", "equation", "math", "+", "*", "divide", "minus", # Math
    "write", "poem", "haiku", "riddle", "story", "script", "code", # Creative/Coding
    "if", "when" # Conditionals
]

# --- Function Definitions (Official JSON Schema) ---
FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "control_light",
            "description": "Controls smart lights - turn on, off, or dim lights in a room",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "The action to perform: on, off, or dim"},
                    "room": {"type": "string", "description": "The room name where the light is located"}
                },
                "required": ["action", "room"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for information using Google",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Sets a countdown timer for a specified duration",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {"type": "string", "description": "Time duration like 5 minutes or 1 hour"},
                    "label": {"type": "string", "description": "Optional timer name or label"}
                },
                "required": ["duration"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Creates a new calendar event or appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The event title"},
                    "date": {"type": "string", "description": "The date of the event"},
                    "time": {"type": "string", "description": "The time of the event"},
                    "description": {"type": "string", "description": "Optional event details"}
                },
                "required": ["title", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_calendar",
            "description": "Reads and retrieves calendar events for a date or time range",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "The date or date range to check"},
                    "filter": {"type": "string", "description": "Optional filter like meetings or appointments"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "passthrough",
            "description": "DEFAULT FUNCTION - Use this whenever no other function is clearly needed. This is the fallback for: greetings (hello, hi, good morning), chitchat (how are you, what's your name), general knowledge questions, explanations, conversations, and ANY query that does NOT explicitly require controlling lights, setting timers, searching the web, or managing calendar events. When in doubt, use passthrough.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thinking": {"type": "boolean", "description": "Set to true for complex reasoning/math/logic, false for simple greetings and chitchat."}
                },
                "required": ["thinking"]
            }
        }
    }
]

# --- Console Colors ---
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
