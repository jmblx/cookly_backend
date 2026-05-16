import json
import logging

from nats.aio.client import Client

logger = logging.getLogger(__name__)


async def send_via_nats(
    nats_client: Client,
    subject: str,
    json_message: str | None = None,
    data: dict | None = None,
    string: str | None = None,
):
    if json_message:
        await nats_client.publish(subject, json_message.encode("utf-8"))
    elif data:
        await nats_client.publish(subject, json.dumps(data).encode("utf-8"))
    elif string:
        await nats_client.publish(subject, string.encode("utf-8"))
