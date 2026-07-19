# AutoClipper

> **YouTube → Short-Form Content Pipeline — Web Edition**

Transform long-form YouTube videos (podcasts, interviews, vlogs) into engaging short-form content (9:16) — powered by AI. Web-based SaaS, self-hosted.

![Platform](https://img.shields.io/badge/platform-Web-blue)
![Frontend](https://img.shields.io/badge/frontend-Expo%20React%20Native-61DAFB)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)

---

## ✨ Features

- **🎥 Auto Download** — Download YouTube videos with subtitles via yt-dlp
- **🔍 AI Highlight Detection** — AI identifies engaging segments (60-120s)
- **✂️ Smart Clipping** — Auto-cut video at optimal timestamps
- **📱 Portrait Conversion** — Landscape (16:9) → Portrait (9:16)
- **🎯 Face Detection** — OpenCV (fast) or MediaPipe (smart speaker tracking)
- **🪝 Hook Generation** — Attention-grabbing intros with TTS voiceover
- **📝 Auto Captions** — Word-by-word highlighted captions (Whisper)
- **📊 SEO Metadata** — Optimized titles & descriptions per clip
- **🖥️ Web SaaS** — Access from anywhere, no install needed

---

## 🏗️ Architecture

```
AUTOCLIPPER-itzset/
├── frontend/          # Expo React Native (Web)
│   ├── src/
│   │   ├── screens/       # 14 pages (Home, Login, Dashboard, etc.)
│   │   ├── components/    # FloatingBottomTab, SkeletonLoader, etc.
│   │   ├── navigation/    # Stack + Tab navigator
│   │   ├── services/      # API client
│   │   └── theme/         # Light/dark/system theme
│   ├── App.tsx
│   └── package.json
│
├── backend/           # FastAPI + Celery
│   ├── app/
│   │   ├── api/           # REST routes
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # AI, video, YouTube services
│   │   └── workers/       # Celery background tasks
│   ├── requirements.txt
│   └── app.py
│
├── README.md
└── .gitignore
```

---

## 🚀 Quick Start (Development)

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| Python | 3.10+ |
| PostgreSQL | 14+ |
| FFmpeg | 4.4+ |
| Redis | 6+ (for Celery) |

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
cp .env.example .env   # edit DB credentials
alembic upgrade head

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npx expo start --web
```

---

## 🌐 Production (Self-Hosted)

Deployed on VPS with:

| Component | Tech |
|-----------|------|
| **Web Server** | Nginx (reverse proxy + static serve) |
| **Frontend** | Expo static build → served by Nginx |
| **Backend** | FastAPI via systemd (`autoclipper-api`) |
| **Background Jobs** | Celery + Redis |
| **Database** | PostgreSQL |
| **SSL** | Let's Encrypt (auto-renew) |

### Deploy

```bash
# Pull latest
git pull origin main

# Build frontend
cd frontend
npm install
npx expo export --platform web
cp -r dist/* /var/www/autoclipper.sir-l.web.id/html/

# Restart backend
sudo systemctl restart autoclipper-api
sudo systemctl restart nginx
```

---

## 📸 Screenshots

| Page | Description |
|------|-------------|
| **Home** | Landing page with app overview |
| **Login** | Email/password authentication |
| **Dashboard** | User dashboard with stats |
| **Create Clip** | Paste YouTube URL, process with AI |
| **Processing** | Real-time progress with animations |
| **Results** | View & download generated clips |
| **Edit Clip** | Fine-tune clip settings |
| **Profile** | User profile & cookie upload |
| **Admin** | User management, queue, system stats |

---

## 🔐 Authentication

- **Email/password** — Register & login
- **YouTube Cookie** — Upload `cookie.json` (refresh_token) to enable clipping
- **Admin** — Manage users, credits, queue monitoring

---

## 🧠 AI Providers

Uses [Novita AI](https://novita.ai) via custom router endpoint. Configurable in backend `.env`.

---

## 📄 License

MIT — see [LICENSE](LICENSE).
