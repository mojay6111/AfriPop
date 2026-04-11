import redis
import json
from app.config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

SESSION_TTL = 175  # 5 seconds buffer before AT 180s timeout
KEY_PREFIX  = "ussd:"


def get_session(session_id: str) -> dict:
    try:
        data = r.get(f"{KEY_PREFIX}{session_id}")
        return json.loads(data) if data else {}
    except Exception as e:
        print(f"Session get failed: {e}")
        return {}


def save_session(session_id: str, data: dict):
    try:
        r.setex(
            f"{KEY_PREFIX}{session_id}",
            SESSION_TTL,
            json.dumps(data)
        )
    except Exception as e:
        print(f"Session save failed: {e}")


def clear_session(session_id: str):
    try:
        r.delete(f"{KEY_PREFIX}{session_id}")
    except Exception as e:
        print(f"Session clear failed: {e}")


def update_session(session_id: str, updates: dict):
    session = get_session(session_id)
    session.update(updates)
    save_session(session_id, session)
