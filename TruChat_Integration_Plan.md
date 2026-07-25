# TruChat - Architecture, Integration Plan & API Specification

## 1. Executive Summary

This document serves as the complete technical specification, API reference, and integration plan for connecting the **TruChat** React frontend (`TruChat/`) to the **Django REST Framework** backend (`app/`). It is created directly based on the codebase analysis of `app/` and the UI design specifications provided in the PDF design document ("AI Editorial Division").

---

## 2. System Architecture Overview

```
+-------------------------------------------------------+
|                    TruChat Frontend                    |
|           (Vite + React 19 + Tailwind CSS)            |
|                   `http://localhost:5173`             |
+-------------------------------------------------------+
                           |
                           | HTTP / REST (JSON) + JWT Bearer Token
                           v
+-------------------------------------------------------+
|                    Django Backend                      |
|           (Django 5.2 + DRF + SimpleJWT)              |
|                   `http://127.0.0.1:8000/api`          |
+-------------------------------------------------------+
          |                                  |
          v                                  v
+-----------------------+          +--------------------+
|  User & Auth App      |          | Data & Claims App  |
|  (/api/user/)         |          | (/api/data/)       |
+-----------------------+          +--------------------+
          |                                  |
          v                                  v
+-----------------------+          +--------------------+
| SQLite / PostgreSQL   |          | LLM & Tavily /     |
| Database              |          | Vector Search      |
+-----------------------+          +--------------------+
```

---

## 3. Backend Analysis & API Endpoint Reference (`app/`)

### 3.1 Authentication & User Endpoints (`/api/user/`)

| Endpoint | Method | Auth Required | Request Payload | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/user/register/` | `POST` | No | `{ email, username, password }` | `{ access_token, refresh_token, token_type, is_verified, verification_email_sent }` | Registers new user account |
| `/api/user/login/` | `POST` | No | `{ email, password }` | `{ access_token, refresh_token, token_type, is_verified }` | Authenticates user and returns JWT pair |
| `/api/user/logout/` | `POST` | Yes (`Bearer`) | `{ refresh_token }` | `{ detail: "Logged out successfully." }` | Blacklists refresh token |
| `/api/user/profile/` | `GET` | Yes (`Bearer`) | None | `{ id, email, username, role, is_verified, date_joined }` | Returns authenticated user profile |
| `/api/user/profile/update/` | `PATCH` | Yes (`Bearer`) | `{ username?, email? }` | Updated profile object | Updates user profile details |
| `/api/user/change-password/` | `POST` | Yes (`Bearer`) | `{ old_password, new_password }` | `{ detail: "Password changed successfully." }` | Changes password |
| `/api/user/forgot-password/` | `POST` | No | `{ email }` | `{ detail: "If the email exists..." }` | Triggers reset email |
| `/api/user/reset-password/` | `POST` | No | `{ uid, token, new_password }` | `{ detail: "Password reset successfully." }` | Completes password reset |
| `/api/user/delete-account/` | `DELETE` | Yes (`Bearer`) | `{ password }` | 204 No Content | Deletes user account |
| `/api/user/google/` | `GET` | No | Query Params | Redirect to Google OAuth | OAuth initiate |
| `/api/user/google/callback/` | `GET` | No | Query Params | Redirect / Auth response | OAuth callback |

### 3.2 Claim Fact-Checking Endpoints (`/api/data/`)

| Endpoint | Method | Auth Required | Request Payload | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/data/claims/check/` | `POST` | No (or Optional) | `{ "claim_text": "..." }` | `{ verdict, confidence_score, credibility_score, explanation }` | Runs fact-checking pipeline against Tavily / LLM |

---

## 4. UI Specification Mapping (from PDF)

The interface follows an **"AI Editorial Division"** aesthetic (cream newsprint background `#F7F4ED`, dark ink typography, structured newspaper borders).

1. **Header & Navigation**:
   - Editorial Banner: `EST. AI EDITORIAL DIVISION`
   - Brand Logo: `Tru Q Chat` / `TRUCHAT` header with subtitle `'Powered by Trusted Sources & Explainable AI'`.
   - Top Bar Links: `VERIFY`, `RECENT VERDICTS`, `Me` (Profile).

2. **Left Sidebar**:
   - Navigation links: `VERIFY NEWS` (active state with red dot indicator), `HISTORY`, `PROFILE`.
   - `TODAY'S VERDICT:` metric counters:
     - `VERIFIED 0`
     - `UNVERIFIED 0`
     - `MISLEADING 0`
   - `Chat History` section.
   - Bottom Action: `[-> Sign out]`.

3. **Center Main Content**:
   - Header Card: `AI Verification Bureau` | `Welcome, <User>` | Subtitle instructions.
   - Example Claim Chips:
     - *"Vaccines secretly contain tracking microchips"*
     - *"WHO confirms 12% drop in global disease burden"*
     - *"Government plans to phase out paper currency by 2028"*
   - Claim Input Area: `ENTER CLAIM FOR VERIFICATION`
     - Textarea with shortcut label: `ENTER TO SUBMIT · SHIFT+ENTER FOR NEW LINE`.
     - `+` button to launch **Attach Article Image or Link** modal.
     - `Verify Claim ->` submit button.

4. **Right Panel**:
   - Header Badge: `BUREAU LIVE` green indicator | `3,847` counter.
   - `How It Works` Card:
     1. *Submit a Claim*
     2. *AI Analysis*
     3. *Receive Report*
   - Caution Notice Card: `⚠ EDITORIAL NOTICE` - AI verdicts are editorial aids, not legal determinations.

5. **Profile Page (`YOUR PROFILE`)**:
   - Account Details Card: User avatar, `Name`, `EMAIL`, `MEMBER SINCE` (D/M/Y), `PLAN` (Free).
   - Sign out button.

---

## 5. Integration Step-by-Step Plan

1. **Clean-up**: Delete duplicate `TruChat/app/` backend directory from the frontend folder.
2. **CORS & Environment Setup**: Update `app/.env` with `CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000`.
3. **Frontend API Layer (`TruChat/src/services/`)**:
   - Configure base URL in `api.js` using `import.meta.env.VITE_API_BASE_URL`.
   - Implement JWT Bearer token request interceptor and automatic token refresh logic.
   - Implement `auth.js` for login, signup, profile, logout calls.
   - Implement `claims.js` for claim verification calls.
4. **Auth Context (`TruChat/src/context/AuthContext.jsx`)**:
   - Manage state for `user`, `accessToken`, `refreshToken`, `loading`.
5. **Component & View Updates**:
   - Wire `Dashboard.jsx`, `MainContent.jsx`, `ClaimInput.jsx`, `RightPanel.jsx`, `VerdictCounter.jsx`, `UploadModal.jsx`, `Profile.jsx`, `Result.jsx`.
6. **Documentation & Testing**: Update `README.md` and verify end-to-end user flows.

---

## 6. Local Setup Instructions

### Backend Setup (`app/`)
```bash
cd app
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend Setup (`TruChat/`)
```bash
cd TruChat
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.
