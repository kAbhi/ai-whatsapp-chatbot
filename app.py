import os
from typing import Dict
from fastapi import FastAPI, Request, Response, HTTPException
import requests
from dotenv import load_dotenv

# Reused from main.py
from anthropic import Anthropic
from claudeConnect import DialogueSession, validate_and_structure_input, anthropic_client

load_dotenv()

app = FastAPI()

# Meta credentials
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secret_token_123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Claude client initialization
# anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
# anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None

# Store dialogue sessions per sender phone number
user_sessions: Dict[str, DialogueSession] = {}

def get_or_create_session(sender: str) -> DialogueSession:
    """Returns an existing session for the user or creates a default one."""
    if sender not in user_sessions:
        default_config = validate_and_structure_input(
            target_audience="General Audience",
            key_message="Deliver helpful, concise, and accurate responses",
            platform="WhatsApp",
            call_to_action="Let us know if you need more help."
        )
        user_sessions[sender] = DialogueSession(
            brand_params=default_config,
            model="claude-opus-5",
            max_history_turns=10
        )
    return user_sessions[sender]

def process_logic(user_text: str, sender: str) -> str:
    clean_text = user_text.strip().lower()

    # Predefined keyword matching
    if "pricing" in clean_text:
        return "Our starter plan is free; standard plans start at $15/month."
    elif "help" in clean_text:
        return "Available commands: 'pricing', 'help', or simply type any message to chat with our assistant."

    # Final fallback: route any other message to Claude
    else:
        if not anthropic_client:
            return "Error: ANTHROPIC_API_KEY is not configured on the server."

        try:
            session = get_or_create_session(sender)
            return session.send_turn(user_text.strip())
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"

def send_whatsapp_message(to_number: str, text: str):
    url = f"https://graph.facebook.com/v26.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }
    requests.post(url, headers=headers, json=payload)

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            sender = msg["from"]

            if msg.get("type") == "text":
                incoming_body = msg["text"]["body"]
                reply_text = process_logic(incoming_body, sender)
                send_whatsapp_message(sender, reply_text)
    except (KeyError, IndexError):
        pass
    return {"status": "ok"}