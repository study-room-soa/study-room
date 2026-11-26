import os
import logging
import httpx

logger = logging.getLogger(__name__)
REVIEW_SERVICE_URL = os.environ["REVIEW_SERVICE_URL"]
client = httpx.Client(base_url=REVIEW_SERVICE_URL, timeout=5.0)

def get_average_rating(room_id: int) -> float | None:
    try:
        response = client.get(
            "/reviews",
            params={"roomId": room_id}
        )

        response.raise_for_status()
        return response.json().get("averageRating")
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("Review Service request failed: %s", error)
        return None