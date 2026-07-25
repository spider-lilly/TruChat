# TruChat - AI Fact-Checking Platform & Verification Bureau

TruChat is a production-grade AI Fact-Checking application featuring a **Django REST Framework** microservice backend and a modern **Vite + React + Tailwind CSS** editorial frontend ("AI Editorial Division" interface).

---

## 📁 Repository Structure

```
check/
├── app/                           # Django REST Framework Backend
│   ├── config/                    # Settings, ASGI/WSGI, and global URLs
│   ├── data/                      # Claim processing pipeline, schemas, & models
│   │   ├── services/
│   │   │   ├── clean.py           # Text cleaning & HTML/Markdown stripping
│   │   │   ├── normalize.py       # Claim entity/keyword normalization
│   │   │   ├── embedding.py       # SentenceTransformer vector embeddings
│   │   │   ├── search.py          # Multi-source search (Tavily, Wikipedia, Wikidata, GDELT)
│   │   │   ├── nli.py             # DeBERTa-v3 NLI zero-shot classification
│   │   │   ├── scoring.py         # Signal-priority verdict aggregation & LLM/rule scoring
│   │   │   ├── cache.py           # Optional Redis Stack vector cache
│   │   │   └── pipeline.py        # End-to-end claim check orchestrator
│   └── user/                      # Authentication & profile management (JWT & Google OAuth)
├── TruChat/                       # Vite + React + Tailwind CSS Frontend
├── requirements.txt               # Backend Python dependencies
├── .gitignore                     # Git exclusion rules
└── README.md                      # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup (`app/`)

1. Open a terminal in the project root directory:
   ```bash
   # Create Python virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Download SpaCy language model (if required)
   python -m spacy download en_core_web_sm
   ```

2. Configure environment variables in `app/.env`:
   ```env
   SECRET_KEY=dev-secret-key-change-in-production
   DEBUG=True
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

   # LLM Provider Configuration (Supports Groq, xAI, OpenAI, Gemini, or OpenRouter)
   # Groq (Free & Fast):
   API_KEY=gsk_your_groq_api_key_here
   LLM_MODEL=llama-3.3-70b-versatile

   # Search API Providers
   TAVILY_API_KEY=your_tavily_api_key_here

   # Optional Redis Vector Cache (Pipeline works automatically if Redis is offline)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. Run migrations and start the Django server:
   ```bash
   cd app
   python manage.py migrate
   python manage.py runserver 8000
   ```
   The backend API will run at `http://127.0.0.1:8000/api/`.

---

### 2. Frontend Setup (`TruChat/`)

1. Open a terminal in the `TruChat/` directory:
   ```bash
   cd TruChat
   npm install
   ```

2. Configure frontend environment variables in `TruChat/.env`:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000/api
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The web application will be accessible at `http://localhost:5173`.

---

## 🤖 Supported LLM Providers for Fact Scoring

The scoring engine dynamically auto-detects your API key type and routes to the appropriate provider:

| Provider | Key Format | Default Model | Base URL |
| :--- | :--- | :--- | :--- |
| **Groq (Free Tier)** | `gsk_...` | `llama-3.3-70b-versatile` | `https://api.groq.com/openai/v1` |
| **xAI Grok** | `xai-...` | `grok-2-1212` | `https://api.x.ai/v1` |
| **Google Gemini** | `AIzaSy...` | `gemini-1.5-flash` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| **OpenRouter (Free)** | `sk-or-...` | `meta-llama/llama-3.2-3b-instruct:free` | `https://openrouter.ai/api/v1` |
| **OpenAI** | `sk-...` | `gpt-4o-mini` | `https://api.openai.com/v1` |

*(Note: If no API key is set or an LLM call fails, the system automatically uses signal-priority NLI rule-based scoring without interrupting request handling.)*

---

## 📡 API Endpoint Reference

### Authentication (`/api/user/`)
- `POST /api/user/register/`: Register user (`{ email, username, password }`).
- `POST /api/user/login/`: Obtain JWT access/refresh token pair (`{ email, password }`).
- `POST /api/user/logout/`: Blacklist token (`{ refresh_token }`).
- `GET /api/user/profile/`: Fetch profile (`Authorization: Bearer <token>`).
- `PATCH /api/user/profile/update/`: Update profile details.
- `POST /api/user/change-password/`: Change password.

### Claim Verification (`/api/data/`)
- `POST /api/data/claims/check/`: Submit claim text for fact-checking (`{ claim_text: "..." }`).
  - Response:
    ```json
    {
      "verdict": "SUPPORTS",
      "confidence_score": 0.94,
      "credibility_score": 0.83,
      "explanation": "Based on evaluation of 6 evidence source(s)..."
    }
    ```

---

## 🔒 Production & Security

- Environment secrets (`.env`), SQLite databases (`*.sqlite3`), and Node dependencies (`node_modules/`) are strictly excluded via `.gitignore`.
- Password verification using Django auth handlers and SimpleJWT blacklisting.
