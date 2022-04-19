from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from api.OAuth2 import get_current_user
from api.websocket.handlers import get_requested_data
from api.websocket.connection import manager
from core.database import get_db

router = APIRouter(
    tags=['WebSocket'],
)

# webpage for websocket testing
with open('./api/websocket/webpage.html') as f:
    html = f.read()


# endpoint to get webpage for websocket testing
@router.get("/websocket")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             # current_user: schemas.TokenData = Depends(get_current_user),
                             db: Session = Depends(get_db), ):
    await manager.connect(websocket)
    try:
        while True:
            request = await websocket.receive_json()
            data = get_requested_data(request, db)
            if data:
                await manager.send_json(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
