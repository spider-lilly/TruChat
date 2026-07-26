# 🛡️ TruChat - AI-Powered Fake News Verification Platform

> Verify before you trust.

TruChat is an AI-powered web application that helps users detect misinformation by verifying news articles, claims, and online content using advanced Natural Language Processing (NLP), Large Language Models (LLMs), and trusted news sources.

Our goal is to promote digital literacy by providing users with quick, reliable, and easy-to-understand fact-checking results.

---

## 🚀 Features

- 🔍 Verify news articles and claims instantly
- 🤖 AI-powered credibility analysis
- 📊 Confidence score for each verification
- 📈 Verification history dashboard
- 🖼️ Image upload support (OCR-ready)
- 🔐 Secure JWT Authentication
- 🌐 Google OAuth Login
- 🔄 Forgot Password & Reset Password
- 👤 User Profile Management
- 📱 Responsive and modern interface

---

## 🧠 Problem Statement

The rapid spread of fake news and misinformation across social media has made it difficult for users to distinguish between factual and misleading information.

TruChat aims to solve this problem by providing an accessible AI-driven platform that analyzes user-submitted content and presents trustworthy verification results with supporting explanations.

---

## 💡 How It Works

1. User logs into the platform.
2. Enter a news article, claim, or URL.
3. Upload an optional supporting image.
4. AI analyzes the content.
5. The platform returns:
   - Credibility Score
   - Confidence Score
   - Verification Status
     - ✅ Verified
     - ⚠️ Misleading
     - ❌ Unverified
   - AI-generated explanation
6. Every verification is stored in the user's history.

---

## 🏗️ Tech Stack

### Frontend

- React.js
- Vite
- Tailwind CSS
- React Router

### Backend

- Django
- Django REST Framework
- JWT Authentication

### AI

- Google Gemini API
- NLP-based content verification

### Database

- SQLite (Development)

### Authentication

- JWT
- Google OAuth

---

## 🎨 UI / UX Design

The complete user interface and user experience were carefully designed using **Figma** before development to ensure a clean, responsive, and intuitive workflow.

The design follows a newspaper/editorial-inspired aesthetic focused on readability, accessibility, and user engagement.

---

## 📂 Project Structure

```
TruChat/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── assets/
│
├── backend/
│   ├── authentication/
│   ├── api/
│   └── manage.py
│
└── README.md
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/FRDARSHIL/TruChat.git
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend

python -m venv venv

# Activate Virtual Environment

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

---

## 📸 Screenshots

> Add screenshots of the Landing Page, Dashboard, Verification Result, and Profile Page here.

---

## 🔮 Future Enhancements

- Browser Extension
- Real-time News Monitoring
- Multi-language Support
- AI Image Deepfake Detection
- Community Fact-Checking
- Citation & Source Verification
- Mobile Application

---

## 👥 Team

- Darshil Agarwal
- Maulya Shetty
- Maansi Dasmohapatra
- Sayan Malik

---

## 📄 License

This project was developed for educational and hackathon purposes.

---

## ⭐ Acknowledgements

- Google Gemini API
- Django REST Framework
- React
- Tailwind CSS
- Vite
- **Figma** (UI/UX Design)
- Open Source Community

---

> **"Think Before You Share. Verify Before You Believe."**
