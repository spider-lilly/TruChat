# TruChat - AI Fact-Checking Platform & Verification Bureau

TruChat is an end-to-end AI Fact-Checking application featuring a **Django REST Framework** backend and a modern **Vite + React** editorial frontend.

---

## 📁 Repository Structure

- `app/`: Django REST Framework backend service handling authentication, claims database, and AI fact-checking pipeline.
- `TruChat/`: Vite + React + Tailwind CSS frontend application ("AI Editorial Division" interface).
- `requirements.txt`: Python package dependencies.
- `TruChat_Integration_Plan.md`: Technical specification and API architecture document.

---

## 🚀 Local Development Setup

### 1. Backend Setup (`app/`)

1. Open a terminal in the root directory:
   ```bash
   # Create and activate Python virtual environment
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. Configure environment variables in `app/.env`:
   ```env
   SECRET_KEY=dev-secret-key-change-in-production
   DEBUG=True
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
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
   The application will be available at `http://localhost:5173`.

---

## 📡 API Endpoint Overview

### User Authentication (`/api/user/`)
- `POST /api/user/register/`: Register a new account (`{ email, username, password }`).
- `POST /api/user/login/`: Login and receive JWT access/refresh token pair (`{ email, password }`).
- `POST /api/user/logout/`: Logout and blacklist token (`{ refresh_token }`).
- `GET /api/user/profile/`: Fetch profile of authenticated user (`Header: Authorization: Bearer <token>`).
- `PATCH /api/user/profile/update/`: Update profile details.
- `POST /api/user/change-password/`: Update user password.
- `POST /api/user/forgot-password/`: Request password reset email.
- `POST /api/user/reset-password/`: Reset user password.
- `DELETE /api/user/delete-account/`: Delete account.

### Claim Verification (`/api/data/`)
- `POST /api/data/claims/check/`: Submit news claim for AI fact-checking verification (`{ claim_text: "..." }`).
  - Response:
    ```json
    {
      "verdict": "SUPPORTS",
      "confidence_score": 0.94,
      "credibility_score": 0.91,
      "explanation": "The available evidence supports the claim."
    }
    ```

---

## 🎨 UI Features (PDF Specification Alignment)

- **Editorial Newspaper Design System**: Cream background (`#F7F4ED`), serif typography, crisp newspaper borders.
- **Interactive Dashboard**:
  - Live Bureau Counter & `How It Works` instructions card.
  - Verdict Counters (`VERIFIED`, `UNVERIFIED`, `MISLEADING`).
  - Quick-select example claims.
  - Keyboard shortcuts (`ENTER` submit / `SHIFT+ENTER` newline).
  - Attach image/link modal popover.
- **Detailed Verdict Reports**: Visual credibility & confidence progress meters with AI explanation breakdown.
- **User Profile Page**: Account details, verification badge, member since date, and logout actions.
