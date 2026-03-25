# Sec-Cam

מערכת מצלמות אבטחה הכוללת:
- `backend` (FastAPI) לניהול מכשירים, פקודות וקבצים
- `frontend` (React + Vite) לממשק ניהול וצפייה
- `pi_agent` (Python) לריצה על Raspberry Pi, קבלת פקודות ושליחת מדיה
- `mediamtx` ל-RTMP/HLS/WebRTC

## Quick Start (Docker)

דרישות:
- Docker + Docker Compose

הרצה:

```bash
docker compose up --build
```

כתובות ברירת מחדל:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- MediaMTX HLS: `http://localhost:8888`

## Pi Agent

### התקנת תלויות

```bash
cd pi_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### הגדרת משתנים

```bash
cp .env.example .env
```

עדכן לפחות את:
- `SERVER_URL` (כתובת ה-backend)
- `DEVICE_ID` (מזהה המכשיר)
- `RTMP_HOST` (בד"כ כתובת שרת ה-mediamtx)

### הרצה

```bash
python main.py
```

## Frontend env

אם צריך API אחר:

```bash
cd frontend
cp .env.example .env
```

## GitHub Readiness

הפרויקט כולל כעת:
- `.gitignore` בשורש (Python/Node/IDE/runtime)
- קבצי `.env.example` ל-`pi_agent` ול-`frontend`
- שמירה על תיקיית `uploads/` עם `.gitkeep`

## Push ראשון ל-GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```
