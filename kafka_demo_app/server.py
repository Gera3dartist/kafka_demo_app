import typing as t
import logging

from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState

from kafka_demo_app.models import AnimalVote
from kafka_demo_app.producer import produce_animal_vote



logger = logging.getLogger(__name__)
app = FastAPI()
app.mount("/static", StaticFiles(directory="fe"))

JSONType = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]] 


@app.on_event("startup")
async def startup_event():
    logger.info("startup event")


@app.get("/")
async def get():
    return FileResponse("fe/index.html")

@app.post("/vote")
async def send_notification(animal: AnimalVote, background_tasks: BackgroundTasks):
    background_tasks.add_task(produce_animal_vote, event=animal.dict())
    return {"message": "Notification sent in the background"}

FE = 'FE'
WORKER = 'WORKER'

class ConnectionManager:
    """
    Idea is to hide choosen protocol behind this manager
    """


    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, connection: WebSocket):
        await connection.accept()
    
    def register_user_connection(self, username: str, connection: WebSocket):
        self.active_connections[username] = connection
        # store the connection details 
        connection.name = username
        connection.otherName = None

    async def send_vote_count(self, data: dict[str, int]):
        if self.active_connections[FE]:
            self.send_message(self.active_connections[FE], {'type': 'vote_count', **data})
        else:
            logger.warning("FE disconnected")
    
    def disconnect(self, connection: WebSocket):
        self.active_connections.pop(connection, None)

    async def send_message(self, connection: WebSocket,  message: dict):
        if connection.client_state == WebSocketState.CONNECTED:
            await connection.send_json(message)

    async def broadcast(self, message: JSONType):
        # TODO: gather
        for connection in self.active_connections.values():
            await self.send_message(connection, message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(connection: WebSocket):
    await connection.accept()
    try:
        while True:

            # data = await connection.receive_text()
            data = await connection.receive_json()
            logger.info(f'>>>{data}')
            a_type = data.get('type')
            match a_type:
                case "vote_count":
                    await manager.send_vote_count(data)
                case "login":
                    await manager.register_user_connection(username=data['name'], connection=connection)
                # default 
                case _:
                    await manager.send_message(connection, { "type": "server_error", "message": "Unrecognized `command`: " + a_type})
    except WebSocketDisconnect as e:
        logger.exception('socket problem')
        manager.disconnect(connection)
        # await manager.broadcast(f"Client #{client_id} left the chat")