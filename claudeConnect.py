import os
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# ============================================================================
# Environment Setup & Client Initialization
# ============================================================================
load_dotenv()
my_api_key = os.getenv("ANTHROPIC_API_KEY")

if not my_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set. Please set it in your .env file.")

anthropic_client = Anthropic(api_key=my_api_key)


# ============================================================================
# Parameter Validation & Setup
# ============================================================================
def validate_and_structure_input(
        target_audience: str,
        key_message: str,
        platform: str = "LinkedIn",
        call_to_action: Optional[str] = None
) -> Dict[str, str]:
    """Validates inputs and structures brand guidelines."""
    inputs = {
        "target_audience": target_audience,
        "key_message": key_message,
        "platform": platform,
        "call_to_action": call_to_action or "No Action by default."
    }

    for field, value in inputs.items():
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"Input validation error: '{field}' cannot be empty.")

    return inputs


# ============================================================================
# Multi-Turn Dialogue Manager
# ============================================================================
class DialogueSession:
    """
    Manages multi-turn conversation state, system prompt anchoring,
    and iterative refinement of social media copy.
    """
    def __init__(self, brand_params: Dict[str, str], model: str = "claude-opus-5", max_history_turns: int = 10):
        self.brand_params = brand_params
        self.model = model
        self.max_history_turns = max_history_turns
        self.messages: List[Dict[str, str]] = []

    def _build_system_prompt(self) -> str:
        """System prompt instructing Claude to mirror the user's tone, language, and conversational style on WhatsApp."""
        return """You are a helpful and natural conversational assistant chatting with a user on WhatsApp.

Your key conversational rules:
1. Mirror Language & Dialect: Always respond in the exact same language and dialect the user uses (e.g., English, Hindi, Hinglish, Spanish, regional slang, or mixed script).
2. Match Tone & Energy: Match the user's tone—if they are informal, casual, or brief, be informal, casual, and brief. If they are formal or direct, match that demeanor.
3. WhatsApp-Friendly Formatting: 
   - Keep answers clean, concise, and easy to skim on mobile screens.
   - Avoid walls of text or unnecessary preamble.
   - Use simple WhatsApp formatting (*bold* for emphasis, short bullet points) only when helpful.
4. Natural Flow: Chat like a real person messaging on WhatsApp—helpful, direct, and engaging without sounding robotic or overly scripted."""

    def _trim_history(self) -> None:
        """Sliding window: retains the most recent turns to maintain token efficiency."""
        # Keep the latest N message pairs (user + assistant)
        max_messages = self.max_history_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

    def send_turn(self, user_instruction: str) -> str:
        """
        Processes a user turn, appends it to conversation history,
        calls the Anthropic API, and captures the assistant response.
        """
        self.messages.append({"role": "user", "content": user_instruction})
        self._trim_history()

        response = anthropic_client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=self._build_system_prompt(),
            messages=self.messages
        )
        print(response)

        # Iterate through content blocks to find the first text block, with fallback
        assistant_reply = ""
        for block in response.content:
            # Check block type or duck-type attribute
            if getattr(block, "type", None) == "text" and hasattr(block, "text"):
                assistant_reply = block.text.strip()
                break
            elif hasattr(block, "text"):
                assistant_reply = str(block.text).strip()
                break

        # Fallback if no text block was detected
        if not assistant_reply:
            assistant_reply = "Some Random Text. There was a problem. I received your message, but couldn't generate a text response."
        # assistant_reply = response.content[0].text.strip()
        self.messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply
