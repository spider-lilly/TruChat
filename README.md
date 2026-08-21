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

## 🎨 UI/UX & Design

The entire TruChat website UI/UX was designed by **Maulya and Maansi**, covering the complete visual experience and user journey across the platform.

The design combines the credibility of a professional **fact-checking and editorial bureau** with the accessibility of a modern AI-powered web application, creating a consistent and intuitive experience throughout TruChat.

### ✨ Design Contributions

- **Complete Website UI/UX:** Designed the entire website interface and user experience across the TruChat platform.
- **Visual Design System:** Defined the layouts, typography, spacing, visual hierarchy, components, and overall design consistency.
- **User Experience:** Designed intuitive user flows for claim submission, verification, authentication, and viewing fact-checking results.
- **Editorial Interface:** Designed the **"AI Editorial Division"** visual experience to establish a professional newsroom/editorial identity.
- **Responsive Design:** Designed responsive layouts for a consistent experience across different screen sizes.
- **Authentication & Profile:** Designed the login, registration, profile, and account management interfaces.
- **Fact-Checking Experience:** Designed the claim submission and verification-result interfaces, including verdicts, confidence scores, credibility scores, and supporting evidence.
- **Frontend Implementation:** The UI/UX designs were translated into the production frontend using **React, Vite, and Tailwind CSS**.

### 👩‍🎨 UI/UX Credits

**UI/UX Design:** Maulya & Maansi  
**Frontend Implementation:** TruChat Development Team

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
