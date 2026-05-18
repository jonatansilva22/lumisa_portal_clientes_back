from collections import defaultdict
from typing import DefaultDict, Set, Tuple

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self):
        self.order_connections: DefaultDict[int, Set[WebSocket]] = defaultdict(set)
        self.direct_connections: DefaultDict[Tuple[int, int], Set[WebSocket]] = defaultdict(set)
        self.user_connections: DefaultDict[int, Set[WebSocket]] = defaultdict(set)

    async def connect_order(self, order_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.order_connections[order_id].add(websocket)

    def disconnect_order(self, order_id: int, websocket: WebSocket) -> None:
        self.order_connections[order_id].discard(websocket)
        if not self.order_connections[order_id]:
            self.order_connections.pop(order_id, None)

    async def connect_direct(self, user1_id: int, user2_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.direct_connections[self._direct_key(user1_id, user2_id)].add(websocket)

    def disconnect_direct(self, user1_id: int, user2_id: int, websocket: WebSocket) -> None:
        key = self._direct_key(user1_id, user2_id)
        self.direct_connections[key].discard(websocket)
        if not self.direct_connections[key]:
            self.direct_connections.pop(key, None)

    async def connect_user(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.user_connections[user_id].add(websocket)

    def disconnect_user(self, user_id: int, websocket: WebSocket) -> None:
        self.user_connections[user_id].discard(websocket)
        if not self.user_connections[user_id]:
            self.user_connections.pop(user_id, None)

    async def broadcast_order(self, order_id: int, payload: dict) -> None:
        await self._broadcast(self.order_connections.get(order_id, set()), payload)

    async def broadcast_direct(self, user1_id: int, user2_id: int, payload: dict) -> None:
        await self._broadcast(
            self.direct_connections.get(self._direct_key(user1_id, user2_id), set()),
            payload,
        )

    async def broadcast_users(self, user_ids: list[int], payload: dict) -> None:
        sockets: Set[WebSocket] = set()
        for user_id in user_ids:
            sockets.update(self.user_connections.get(user_id, set()))
        await self._broadcast(sockets, payload)

    async def _broadcast(self, sockets: Set[WebSocket], payload: dict) -> None:
        disconnected = []
        for socket in list(sockets):
            try:
                await socket.send_json(payload)
            except RuntimeError:
                disconnected.append(socket)

        for socket in disconnected:
            sockets.discard(socket)

    @staticmethod
    def _direct_key(user1_id: int, user2_id: int) -> Tuple[int, int]:
        return tuple(sorted((user1_id, user2_id)))


chat_manager = ChatConnectionManager()