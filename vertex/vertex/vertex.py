import base64
from typing import Optional
import uuid
from vertex import service


async def get_receiver(sender_id: uuid.UUID):
    params = {
        'select': 'vertex.receiver(id,func)', 'sender': f'eq.{sender_id}'}
    status, connections = await service.DB('vertex_connection').get(params=params)
    return status, connections


def wrap_correlation_id(data: Optional[bytes]) -> bytes:
    return base64.b64encode(data or uuid.uuid4().bytes)


def unwrap_correlation_id(correlation_id: bytes) -> Optional[bytes]:
    if len(correlation_id) == 16:
        return None
    return base64.b64decode(correlation_id)
