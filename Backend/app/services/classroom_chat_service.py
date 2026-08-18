import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional
from fastapi import WebSocket
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClassroomChatManager:
    """
    Quản lý kết nối WebSocket và Pub/Sub theo phòng học (classroom_id).
    Hỗ trợ multi-instance scaling qua Redis Pub/Sub và theo dõi người dùng online.
    """
    def __init__(self):
        # Identify this backend process so Redis messages published by this
        # process are not broadcast to its local sockets for a second time.
        self.instance_id = uuid.uuid4().hex
        # classroom_id -> set of active WebSockets on THIS process
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # classroom_id -> { websocket: user_id }
        self.connection_users: Dict[int, Dict[WebSocket, int]] = {}
        # classroom_id -> set of online user_ids
        self.online_users: Dict[int, Set[int]] = {}
        
        # Lock for local state mutations
        self.lock = asyncio.Lock()
        
        # Redis async pub/sub task management
        self.redis_client: Optional[aioredis.Redis] = None
        self.pubsub_tasks: Dict[int, asyncio.Task] = {}

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        """Lazy initialization of async Redis client."""
        if self.redis_client is None:
            try:
                self.redis_client = aioredis.from_url(
                    settings.REDIS_URL, decode_responses=True
                )
            except Exception as e:
                logger.warning("Không thể khởi tạo async Redis client cho Chat Manager: %s", e)
                return None
        return self.redis_client

    async def connect(self, classroom_id: int, websocket: WebSocket, user_id: int) -> bool:
        """Đăng ký kết nối WebSocket mới và bắt đầu lắng nghe Redis Pub/Sub nếu cần."""
        async with self.lock:
            if classroom_id not in self.active_connections:
                self.active_connections[classroom_id] = set()
                self.connection_users[classroom_id] = {}
                self.online_users[classroom_id] = set()

            user_connection_count = sum(
                1 for uid in self.connection_users[classroom_id].values() if uid == user_id
            )
            if user_connection_count >= 3:
                return False

            self.active_connections[classroom_id].add(websocket)
            self.connection_users[classroom_id][websocket] = user_id
            self.online_users[classroom_id].add(user_id)

            # Start Redis PubSub listener task for this classroom if not started
            if classroom_id not in self.pubsub_tasks:
                task = asyncio.create_task(self._listen_redis_channel(classroom_id))
                self.pubsub_tasks[classroom_id] = task

        # Broadcast online presence update
        await self.broadcast_online_users(classroom_id)
        return True

    async def disconnect(self, classroom_id: int, websocket: WebSocket):
        """Hủy kết nối WebSocket và cập nhật danh sách Online Users."""
        async with self.lock:
            if classroom_id in self.active_connections:
                user_id = self.connection_users[classroom_id].pop(websocket, None)
                self.active_connections[classroom_id].discard(websocket)

                # Check if user has any remaining active tabs/sockets in this room
                if user_id:
                    user_still_connected = any(
                        uid == user_id for uid in self.connection_users[classroom_id].values()
                    )
                    if not user_still_connected:
                        self.online_users[classroom_id].discard(user_id)

                if not self.active_connections[classroom_id]:
                    del self.active_connections[classroom_id]
                    del self.connection_users[classroom_id]
                    self.online_users.pop(classroom_id, None)

                    # Cancel Redis listener task when room is empty on this server
                    if classroom_id in self.pubsub_tasks:
                        task = self.pubsub_tasks.pop(classroom_id)
                        task.cancel()

        # Broadcast updated online status
        await self.broadcast_online_users(classroom_id)

    async def broadcast_local(self, classroom_id: int, payload: dict):
        """Gửi dữ liệu tới tất cả WebSocket kết nối tại tiến trình này."""
        async with self.lock:
            connections = list(self.active_connections.get(classroom_id, set()))

        if not connections:
            return

        async def safe_send(ws: WebSocket):
            try:
                await ws.send_json(payload)
            except Exception as exc:
                logger.debug("Lỗi khi gửi WebSocket message: %s", exc)

        await asyncio.gather(*(safe_send(ws) for ws in connections), return_exceptions=True)

    async def broadcast(self, classroom_id: int, payload: dict):
        """
        Deliver locally first, then publish to other backend processes.

        Local delivery must not depend on Redis Pub/Sub. A subscriber can be
        starting or reconnecting while a message is published; previously that
        race caused the message to be committed to MySQL but not displayed
        until the client reloaded its history.
        """
        await self.broadcast_local(classroom_id, payload)

        r = await self._get_redis()
        channel = f"classroom_chat_{classroom_id}"
        message_str = json.dumps({
            "source_instance": self.instance_id,
            "payload": payload,
        })

        if r:
            try:
                await r.publish(channel, message_str)
                return
            except Exception as e:
                logger.warning("Lỗi Redis Publish; tin nhắn đã được phát local: %s", e)

    async def broadcast_online_users(self, classroom_id: int):
        """Broadcast danh sách user_id đang online trong phòng."""
        async with self.lock:
            online_ids = list(self.online_users.get(classroom_id, set()))

        payload = {
            "type": "online_presence",
            "classroom_id": classroom_id,
            "online_user_ids": online_ids,
            "online_count": len(online_ids)
        }
        await self.broadcast(classroom_id, payload)

    async def _listen_redis_channel(self, classroom_id: int):
        """Listen to Redis Pub/Sub and reconnect while the local room is active."""
        channel = f"classroom_chat_{classroom_id}"

        while True:
            async with self.lock:
                room_is_active = bool(self.active_connections.get(classroom_id))
            if not room_is_active:
                return

            r = await self._get_redis()
            if not r:
                await asyncio.sleep(1)
                continue

            pubsub = r.pubsub()
            try:
                await pubsub.subscribe(channel)
                async for message in pubsub.listen():
                    if message["type"] != "message":
                        continue
                    try:
                        decoded = json.loads(message["data"])
                        # New envelope format. Ignore our own publication
                        # because it was already delivered locally above.
                        if "payload" in decoded and "source_instance" in decoded:
                            if decoded["source_instance"] == self.instance_id:
                                continue
                            payload = decoded["payload"]
                        else:
                            # Backward compatibility during rolling deploys.
                            payload = decoded
                        await self.broadcast_local(classroom_id, payload)
                    except Exception as err:
                        logger.error("Lỗi parse JSON từ Redis Pub/Sub: %s", err)
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logger.warning(
                    "Redis Pub/Sub phòng %s bị gián đoạn, thử kết nối lại: %s",
                    classroom_id,
                    exc,
                )
                await asyncio.sleep(1)
            finally:
                try:
                    await pubsub.aclose()
                except Exception:
                    pass


classroom_chat_manager = ClassroomChatManager()
