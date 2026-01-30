import requests
import os

BASE_URL = "https://api.zoom.us/v2"

def get_zoom_access_token(code: str):
    url = "https://zoom.us/oauth/token"
    resp = requests.post(url, params={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/api/zoom/oauth/callback",
    }, auth=("H5obNZUfTleOSlaDb9zDA","pCVGqqWemj4r6W2KUco4INTVA0bjSebH"))

    resp.raise_for_status()
    return resp.json()


def create_zoom_meeting(access_token: str, topic: str, datetime: str):
    url = f"{BASE_URL}/users/me/meetings"

    payload = {
        "topic": topic,
        "type": 2,
        "start_time": datetime,
        "duration": 30,  # minutes
        "timezone": "UTC",
        "settings": {
            "join_before_host": True,
            "approval_type": 0
        }
    }

    resp = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    resp.raise_for_status()
    return resp.json()
