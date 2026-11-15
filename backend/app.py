import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from database import get_snapshots, init_db, save_daily_snapshot, save_profile_snapshot, save_reels_snapshot
from instagram import build_reel_payload, exchange_code_for_token, exchange_token_for_long_lived, get_account_insights, get_business_account_id, get_media, get_oauth_url, get_profile, refresh_long_lived_token

load_dotenv()

app = Flask(__name__)
allowed_origins = [
    origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",") if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
DB_PATH = Path(os.getenv("DB_PATH", "instance/rohan.sqlite3"))

DEMO_PROFILE = {
    "username": "lilboy.rohan",
    "name": "Rohan Halder",
    "profile_image_url": "",
    "followers": 12800,
    "total_likes": 86400,
    "total_reels": 42,
    "total_views": 1200000,
}

DEMO_REELS = [
    {
        "id": "demo-1",
        "title": "Midnight Miles",
        "caption": "Some roads feel like they understand you. 🖤",
        "song": "Demo track · Night Drive",
        "views": 128000,
        "likes": 9400,
        "date": "2026-11-08",
        "thumbnail_url": "",
    },
    {
        "id": "demo-2",
        "title": "Blue Hour Ride",
        "caption": "Chasing the last light of the day 💙",
        "song": "Demo track · Blue Hour",
        "views": 96000,
        "likes": 7100,
        "date": "2026-10-27",
        "thumbnail_url": "",
    },
    {
        "id": "demo-3",
        "title": "Ride With Heart",
        "caption": "Two wheels, one heart, endless roads 💚",
        "song": "Demo track · Ride With Me",
        "views": 214000,
        "likes": 18000,
        "date": "2026-10-12",
        "thumbnail_url": "",
    },
]

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "mode": "demo" if DEMO_MODE else "instagram"})

@app.get("/api/oauth/url")
def oauth_url():
    return jsonify({"url": get_oauth_url()})

@app.get("/api/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing code"}), 400

    short_lived = exchange_code_for_token(code)
    long_lived = exchange_token_for_long_lived(short_lived.get("access_token"))
    refreshed = refresh_long_lived_token(long_lived.get("access_token"))

    os.environ["INSTAGRAM_ACCESS_TOKEN"] = refreshed.get("access_token", long_lived.get("access_token"))
    os.environ["INSTAGRAM_REFRESH_TOKEN"] = refreshed.get("refresh_token", long_lived.get("access_token"))

    return jsonify({
        "message": "Token generated successfully.",
        "expires_in": refreshed.get("expires_in"),
        "access_token": refreshed.get("access_token"),
        "refresh_token": refreshed.get("refresh_token"),
    })

@app.get("/api/profile")
def public_profile():
    if DEMO_MODE:
        return jsonify({"profile": DEMO_PROFILE, "mode": "demo"})

    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not access_token:
        return jsonify({"profile": DEMO_PROFILE, "mode": "demo"})

    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID") or get_business_account_id(access_token)
    profile = get_profile(access_token, account_id)
    payload = {
        "username": profile.get("username"),
        "name": profile.get("name"),
        "profile_image_url": profile.get("profile_picture_url"),
        "followers": profile.get("followers_count"),
        "total_likes": 0,
        "total_reels": profile.get("media_count"),
        "total_views": 0,
    }
    save_profile_snapshot(payload, DB_PATH)
    return jsonify({"profile": payload, "mode": "instagram"})

@app.get("/api/reels")
def public_reels():
    if DEMO_MODE:
        return jsonify({"items": DEMO_REELS, "mode": "demo"})

    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not access_token:
        return jsonify({"items": DEMO_REELS, "mode": "demo"})

    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID") or get_business_account_id(access_token)
    media = get_media(access_token, account_id, limit=12)
    payload = build_reel_payload(access_token, media)
    save_reels_snapshot(payload, DB_PATH)
    return jsonify({"items": payload, "mode": "instagram"})

@app.get("/api/analytics")
def public_analytics():
    if DEMO_MODE:
        return jsonify({"days": get_snapshots(15, DB_PATH), "mode": "demo"})

    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not access_token:
        return jsonify({"days": get_snapshots(15, DB_PATH), "mode": "demo"})

    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID") or get_business_account_id(access_token)
    insights = get_account_insights(access_token, account_id)
    save_daily_snapshot(insights, DB_PATH)
    return jsonify({"days": get_snapshots(15, DB_PATH), "mode": "instagram"})


if __name__ == "__main__":
    init_db(DB_PATH)
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
