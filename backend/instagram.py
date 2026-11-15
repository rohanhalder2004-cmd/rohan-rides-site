import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

META_GRAPH_BASE = "https://graph.facebook.com/v20.0"


def get_oauth_url() -> str:
    params = {
        "client_id": INSTAGRAM_APP_ID,
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "scope": "instagram_business_basic,instagram_business_content_publish,instagram_business_manage_comments,instagram_business_manage_messages",
        "response_type": "code",
    }
    query = "&".join(f"{key}={value}" for key, value in params.items())
    return f"https://api.instagram.com/oauth/authorize?{query}"


def exchange_code_for_token(code: str) -> Dict[str, Any]:
    response = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": INSTAGRAM_APP_ID,
            "client_secret": INSTAGRAM_APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": INSTAGRAM_REDIRECT_URI,
            "code": code,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def exchange_token_for_long_lived(short_lived_token: str) -> Dict[str, Any]:
    response = requests.get(
        f"{META_GRAPH_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": INSTAGRAM_APP_ID,
            "client_secret": INSTAGRAM_APP_SECRET,
            "fb_exchange_token": short_lived_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def refresh_long_lived_token(long_lived_token: str) -> Dict[str, Any]:
    response = requests.get(
        f"{META_GRAPH_BASE}/refresh_access_token",
        params={
            "grant_type": "ig_refresh_token",
            "access_token": long_lived_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_business_account_id(access_token: str) -> str:
    response = requests.get(
        f"{META_GRAPH_BASE}/me/accounts",
        params={
            "fields": "instagram_business_account{id,username,name}",
            "access_token": access_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    for page in data.get("data", []):
        account = page.get("instagram_business_account")
        if account and account.get("id"):
            return account["id"]
    raise ValueError("No Instagram business account found.")


def get_profile(access_token: str, account_id: str) -> Dict[str, Any]:
    response = requests.get(
        f"{META_GRAPH_BASE}/{account_id}",
        params={
            "fields": "id,username,account_type,media_count,followers_count,follows_count,profile_picture_url,name",
            "access_token": access_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_media(access_token: str, account_id: str, limit: int = 12) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{META_GRAPH_BASE}/{account_id}/media",
        params={
            "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp",
            "access_token": access_token,
            "limit": limit,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def get_media_insights(access_token: str, media_id: str) -> Dict[str, Any]:
    response = requests.get(
        f"{META_GRAPH_BASE}/{media_id}/insights",
        params={
            "metric": "reach,plays,likes,comments,shares,saved",
            "access_token": access_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_account_insights(access_token: str, account_id: str) -> Dict[str, Any]:
    response = requests.get(
        f"{META_GRAPH_BASE}/{account_id}/insights",
        params={
            "metric": "reach,views,profile_views,follower_count",
            "period": "day",
            "access_token": access_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def normalize_media(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": item.get("id"),
        "caption": item.get("caption", ""),
        "media_type": item.get("media_type", "VIDEO"),
        "media_url": item.get("media_url"),
        "thumbnail_url": item.get("thumbnail_url"),
        "permalink": item.get("permalink"),
        "timestamp": item.get("timestamp"),
    }


def build_reel_payload(access_token: str, media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payload = []
    for media in media_items:
        item = normalize_media(media)
        try:
            insights = get_media_insights(access_token, media["id"])
            totals = {}
            for metric in insights.get("data", []):
                if "total_value" in metric:
                    totals[metric["name"]] = metric["total_value"].get("value")
                elif "values" in metric and metric["values"]:
                    totals[metric["name"]] = metric["values"][-1].get("value")
            item["views"] = totals.get("views", totals.get("plays", 0))
            item["likes"] = totals.get("likes", 0)
        except Exception:
            item["views"] = 0
            item["likes"] = 0
        payload.append(item)
    return payload
