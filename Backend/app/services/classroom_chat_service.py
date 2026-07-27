import asyncio
import json
import logging
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

    async def connect(self, classroom_id: int, websocket: WebSocket, user_id: int):
        """Đăng ký kết nối WebSocket mới và bắt đầu lắng nghe Redis Pub/Sub nếu cần."""
        async with self.lock:
            if classroom_id not in self.active_connections:
                self.active_connections[classroom_id] = set()
                self.connection_users[classroom_id] = {}
                self.online_users[classroom_id] = set()

            self.active_connections[classroom_id].add(websocket)
            self.connection_users[classroom_id][websocket] = user_id
            self.online_users[classroom_id].add(user_id)

            # Start Redis PubSub listener task for this classroom if not started
            if classroom_id not in self.pubsub_tasks:
                task = asyncio.create_task(self._listen_redis_channel(classroom_id))
                self.pubsub_tasks[classroom_id] = task

        # Broadcast online presence update
        await self.broadcast_online_users(classroom_id)

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
        Publish thông điệp lên Redis Pub/Sub channel.
        Tất cả các server instance sẽ nhận tin nhắn từ Redis và broadcast cho client của họ.
        """
        r = await self._get_redis()
        channel = f"classroom_chat_{classroom_id}"
        message_str = json.dumps(payload)

        if r:
            try:
                await r.publish(channel, message_str)
                return
            except Exception as e:
                logger.warning("Lỗi Redis Publish, fallback sang local broadcast: %s", e)

        # Fallback to local process broadcast if Redis fails
        await self.broadcast_local(classroom_id, payload)

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
        """Background task lắng nghe tin nhắn từ kênh Pub/Sub Redis của phòng."""
        r = await self._get_redis()
        if not r:
            return

        pubsub = r.pubsub()
        channel = f"classroom_chat_{classroom_id}"

        try:
            await pubsub.subscribe(channel)
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        payload = json.loads(message["data"])
                        await self.broadcast_local(classroom_id, payload)
                    except Exception as err:
                        logger.error("Lỗi parse JSON từ Redis Pub/Sub: %s", err)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception as exc:
            logger.error("Lỗi Redis PubSub Listener phòng %s: %s", classroom_id, exc)
        finally:
            try:
                await pubsub.close()
            except Exception:
                pass


classroom_chat_manager = ClassroomChatManager()

