# Rohan Halder — Bike Ride Reel Website

A responsive personal website for an Instagram bike-rides creator. This project includes a dark racing-inspired UI, 3D intro portrait, reel showcase, analytics dashboard, and an Instagram-ready backend that works in demo mode until credentials are configured.

## Project structure

```text
rohan-rides-site/
├── frontend/
│   ├── index.html
│   ├── assets/
│   │   └── placeholder-portrait.svg
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── intro3d.js
│       ├── reels.js
│       └── analytics.js
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── instagram.py
│   ├── requirements.txt
│   ├── .env.example
│   └── render.yaml
├── .gitignore
└── README.md
```

## Frontend preview

From the project root:

```bash
cd frontend
python -m http.server 8000
```

Open:

```text
http://localhost:8000
```

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

App preview:

```text
http://127.0.0.1:5000/api/health
```

## Instagram setup

To make the site live with real Instagram data, configure these values in `backend/.env`:

```dotenv
DEMO_MODE=false
CORS_ORIGINS=http://localhost:8000
DB_PATH=instance/rohan.sqlite3
HOST=127.0.0.1
PORT=5000
FLASK_DEBUG=true

INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
INSTAGRAM_REDIRECT_URI=http://127.0.0.1:5000/api/oauth/callback
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_REFRESH_TOKEN=
INSTAGRAM_ACCOUNT_ID=
```

Then set up the Meta app and Instagram Professional account in the backend flow. The app will fetch reels and analytics from the Instagram Graph API, cache them in SQLite, and serve the frontend via `/api/profile`, `/api/reels`, and `/api/analytics`.

## Deployment

### Frontend on GitHub Pages
- push the `frontend/` files to a GitHub Pages branch or folder
- enable Pages from the repo settings

### Backend on Render
- connect the `backend/` folder as a web service
- set env variables from `.env`
- use:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

## Notes
- The site ships in demo mode by default, so it works without live API credentials.
- To replace the placeholder portrait, upload a final profile image to `frontend/assets/placeholder-portrait.svg` or swap the loader target in `frontend/js/intro3d.js` to a real image file.
- Real Instagram data requires a valid Meta app, a Professional account, and secure backend token storage.
