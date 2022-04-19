from fastapi import WebSocket


class ConnectionMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConnectionMeta, cls).__call__(*args, **kwargs)
        return cls._instance


class ConnectionManager(metaclass=ConnectionMeta):

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, data: str, websocket: WebSocket):
        await websocket.send_text(data)

    async def send_json(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    async def send_bytes(self, data: bytes, websocket: WebSocket):
        await websocket.send_bytes(data)


manager = ConnectionManager()
