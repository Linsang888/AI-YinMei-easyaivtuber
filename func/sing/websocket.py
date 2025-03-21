import asyncio
import websockets
from func.log.default_log import DefaultLog
from websockets.exceptions import InvalidMessage


class WebSocketServer:
    # 设置控制台日志
    log = DefaultLog().getLogger()

    def __init__(self, host="localhost", port=18765):
        self.host = host
        self.port = port
        self.clients = set()  # 存储所有连接的客户端

    async def handle_client(self, websocket):
        # 新的客户端连接
        self.clients.add(websocket)
        self.log.info(f"新的客户端连接: {websocket.remote_address}")
        try:
            async for message in websocket:
                self.log.info(f"收到消息: {message}")
                # 回显消息给客户端
                await websocket.send(f"服务器已收到: {message}")
        except InvalidMessage as e:
            # 捕获无效的 HTTP 请求异常
            self.log.error(f"无效的 HTTP 请求: {e}")
            await websocket.close(code=1002, reason="Invalid HTTP request")  # 关闭连接
        except websockets.ConnectionClosed as e:
            self.log.info(f"客户端断开连接: {e}")
        finally:
            # 移除断开的客户端
            self.clients.remove(websocket)
            self.log.info(f"客户端已移除: {websocket.remote_address}")

    async def send(self, message):
        """向所有连接的客户端发送消息"""
        if not self.clients:
            self.log.info("没有客户端连接，无法发送消息")
            return
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.ConnectionClosed:
                disconnected_clients.add(client)
        # 清理已断开的客户端
        self.clients -= disconnected_clients

    async def start(self):
        self.log.info(f"启动 WebSocket 服务器: ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # 持续运行直到手动停止