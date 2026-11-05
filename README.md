# 💬 Autonomous Multi-Persona WhatsApp AI Chatbot

A stateful, production-ready WhatsApp agent engineered to explore **LLM steerability, dynamic persona adaptation, and prompt sampling dynamics** in real-world conversational messaging. 

Integrated with the **Meta WhatsApp Cloud API** and Anthropic's **Claude API** (with extended thinking/reasoning blocks enabled), this system acts as a testbed for evaluating how sampling parameters ($\text{temperature}$, $\text{top\_p}$, and system-prompt conditioning) affect multi-turn conversational nuance, cultural tone adaptation, and latency under messaging constraints.

---

## ⚡ Key Highlights & Architecture

- **Meta WhatsApp Cloud API Integration**: Direct webhook ingestion with signature verification (`X-Hub-Signature-256`), idempotent event handling, and asynchronous outbound dispatch.
- **Dynamic Parameter Tuning & Persona Steerability**: Systematically alters temperature, top-p, and system instruction constraints to observe behavioral shifts across diverse cultural archetypes, colloquial phrasing, and empathetic reasoning.
- **Thinking / Extended Reasoning Support**: Hooks into Claude's thinking blocks to evaluate complex multi-turn logic and ambiguous intent resolution prior to response generation.
- **Sliding-Window State Management**: In-memory session tracking with automated token truncation, preserving conversational context without overflowing window budgets or inflating inference latency.
- **Fault-Tolerant Webhook Architecture**: Decouples incoming message acknowledgment ($200\text{ OK}$) from downstream inference pipelines to prevent webhook timeout drops and duplicate message loops.

---

## 🛠️ Architecture & Request Flow

```
[User Message via WhatsApp]
           │
           ▼
[Meta WhatsApp Cloud API Gateway]
           │  (HTTPS POST Webhook)
           ▼
[FastAPI / Webhook Server]
   ├── HMAC Signature Verification
   ├── Idempotency Check (Message Deduplication)
   └── Session & State Manager (Sliding-Window History)
           │
           ▼
[LLM Inference Engine]
   ├── Dynamic Persona & Tone Selector
   ├── Parameter Modulation (temperature, top_p, max_tokens)
   └── Claude API (with Thinking Blocks)
           │
           ▼
[Outbound Dispatcher] ──▶ [WhatsApp Graph API] ──▶ [User WhatsApp Client]
```

---

## 🚀 Tech Stack

- **Runtime & Framework**: Python 3.10+, FastAPI / Uvicorn (or Flask)
- **AI / LLM Integration**: Anthropic Claude API (`anthropic` SDK), prompt orchestration
- **Messaging Gateway**: Meta for Developers — WhatsApp Business Cloud API
- **State & Caching**: In-Memory Session Storage / Redis-compatible interface
- **Tooling & Profiling**: `python-dotenv`, Pydantic for payload validation, Requests/HTTPX

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file in the project root:

```bash
# Meta WhatsApp Cloud API Credentials
WHATSAPP_TOKEN=your_meta_system_user_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_webhook_verify_token

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Sampling & Steerability Defaults
LLM_DEFAULT_TEMPERATURE=0.7
LLM_DEFAULT_TOP_P=0.9
MAX_CONTEXT_TURNS=10
```

---

## 📦 Quickstart

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/kAbhi/ai-whatsapp-chatbot.git
cd ai-whatsapp-chatbot

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Webhook Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Expose Locally (For Testing Meta Webhooks)

Use Ngrok or Cloudflare Tunnels to expose your local port:

```bash
ngrok http 8000
```

In your **Meta App Dashboard** > **WhatsApp** > **Configuration**:
- **Callback URL**: `https://<your-ngrok-domain>/webhook`
- **Verify Token**: Value from your `WHATSAPP_VERIFY_TOKEN`
- Subscribe to the `messages` webhook field.

---

## 🧪 Experiments in LLM Steerability

This project focuses on evaluating how continuous parameter variations alter conversational performance:

| Parameter Varied | Observation & Focus Area |
| :--- | :--- |
| **$\text{Temperature } (0.2 \rightarrow 0.9)$** | Lower values anchor strict factual Q&A; higher values significantly increase colloquial warmth, humor, and natural conversational cadence. |
| **Thinking Blocks** | Evaluates whether pre-response reasoning reduces hallucination on complex, multi-constraint personal queries inside an informal chat medium. |
| **Context Pruning** | Balancing user memory retention against token latency to keep round-trip response times within conversational tolerance ($< 2.5\text{s}$). |

---

## 📄 License

MIT License. Feel free to use and experiment!