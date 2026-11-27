import os
import logging
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)
USER_SERVICE_URL = os.environ["USER_SERVICE_URL"]
NOTIFICATION_SERVICE_URL = os.environ["NOTIFICATION_SERVICE_URL"]

client = httpx.Client(timeout=5.0)

def check_user_exists(user_id: int, authorization: str):
    try:
        response = client.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers={"Authorization": authorization}
        )

        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        response.raise_for_status()
    except httpx.HTTPError as error:
        logger.warning("User Service request failed: %s", error)
        raise HTTPException(
            status_code=503,
            detail="User Service unavailable"
        )

def send_notification(
    user_id: int, 
    message: str,
    authorization: str
):
    try:
        response = client.post(
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            json={
                "userId": user_id,
                "message": message
            },
            headers={"Authorization": authorization}
        )

        response.raise_for_status()
    except httpx.HTTPError as error:
        logger.warning(
            "Notification Service request failed: %s",
            error
        )