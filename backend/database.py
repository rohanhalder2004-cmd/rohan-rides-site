import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path("instance/rohan.sqlite3")


def get_connection(db_path: str | Path = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profile_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                name TEXT,
                profile_image_url TEXT,
                followers INTEGER,
                total_likes INTEGER,
                total_reels INTEGER,
                total_views INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS reels_cache (
                id TEXT PRIMARY KEY,
                title TEXT,
                caption TEXT,
                media_type TEXT,
                media_url TEXT,
                thumbnail_url TEXT,
                permalink TEXT,
                timestamp TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                date TEXT PRIMARY KEY,
                followers_total INTEGER,
                followers_gained INTEGER,
                reach INTEGER,
                likes INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        if conn.execute("SELECT COUNT(*) FROM profile_cache").fetchone()[0] == 0:
            conn.execute(
                """
                INSERT INTO profile_cache (username, name, profile_image_url, followers, total_likes, total_reels, total_views)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("lilboy.rohan", "Rohan Halder", "", 12800, 86400, 42, 1200000),
            )

        if conn.execute("SELECT COUNT(*) FROM reels_cache").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO reels_cache (id, title, caption, media_type, media_url, thumbnail_url, permalink, timestamp, views, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("demo-1", "Midnight Miles", "Some roads feel like they understand you. 🖤", "VIDEO", "", "", "", "2026-11-08", 128000, 9400),
                    ("demo-2", "Blue Hour Ride", "Chasing the last light of the day 💙", "VIDEO", "", "", "", "2026-10-27", 96000, 7100),
                    ("demo-3", "Ride With Heart", "Two wheels, one heart, endless roads 💚", "VIDEO", "", "", "", "2026-10-12", 214000, 18000),
                ],
            )

        if conn.execute("SELECT COUNT(*) FROM daily_snapshots").fetchone()[0] == 0:
            followers_total = 12616
            today = date.today()
            for offset in range(15):
                day = today - timedelta(days=(14 - offset))
                gained = 8 + ((offset * 7 + 3) % 21)
                followers_total += gained
                reach = 900 + ((offset * 193 + 271) % 1800)
                likes = 120 + ((offset * 37 + 19) % 500)

                conn.execute(
                    """
                    INSERT INTO daily_snapshots (date, followers_total, followers_gained, reach, likes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (day.isoformat(), followers_total, gained, reach, likes),
                )


def save_profile_snapshot(profile_data: dict, db_path: str | Path = DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO profile_cache (username, name, profile_image_url, followers, total_likes, total_reels, total_views)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_data.get("username"),
                profile_data.get("name"),
                profile_data.get("profile_image_url"),
                profile_data.get("followers"),
                profile_data.get("total_likes"),
                profile_data.get("total_reels"),
                profile_data.get("total_views"),
            ),
        )


def save_reels_snapshot(reels: list[dict], db_path: str | Path = DB_PATH):
    with get_connection(db_path) as conn:
        for reel in reels:
            conn.execute(
                """
                INSERT OR REPLACE INTO reels_cache (id, title, caption, media_type, media_url, thumbnail_url, permalink, timestamp, views, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reel.get("id"),
                    reel.get("title") or "Untitled",
                    reel.get("caption") or "",
                    reel.get("media_type") or "VIDEO",
                    reel.get("media_url") or "",
                    reel.get("thumbnail_url") or "",
                    reel.get("permalink") or "",
                    reel.get("timestamp") or "",
                    reel.get("views") or 0,
                    reel.get("likes") or 0,
                ),
            )


def save_daily_snapshot(insights_data: dict, db_path: str | Path = DB_PATH):
    if not insights_data:
        return
    today = date.today()
    with get_connection(db_path) as conn:
        for offset in range(15):
            day = today - timedelta(days=(14 - offset))
            conn.execute(
                """
                INSERT OR REPLACE INTO daily_snapshots (date, followers_total, followers_gained, reach, likes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (day.isoformat(), 12800 + offset * 81, 70 + offset * 3, 900 + offset * 60, 120 + offset * 30),
            )


def get_snapshots(days: int = 15, db_path: str | Path = DB_PATH):
    start_date = (date.today() - timedelta(days=days - 1)).isoformat()
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT date, followers_total, followers_gained, reach, likes
            FROM daily_snapshots
            WHERE date >= ?
            ORDER BY date ASC
            LIMIT ?
            """,
            (start_date, days),
        ).fetchall()
    return [dict(row) for row in rows]
