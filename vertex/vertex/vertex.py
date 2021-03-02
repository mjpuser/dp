from uuid import UUID
from vertex import service


async def receiver(sender_id: UUID):
    params = {'select': 'vertex.receiver(id,func)', 'sender': f'eq.{sender_id}'}
    status, connections = await service.DB('vertex_connection').get(params=params)
    return status, connections
