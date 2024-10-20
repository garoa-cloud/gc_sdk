import asyncio

from gc_sdk import rpc
import uvicorn
from apps import FileApp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


class NodeManager:
    def __init__(self):
        self.nodes = []

    def list_nodes(self) -> list[rpc.Target]:
        return self.nodes

    def add_node(self, *, node: rpc.Target):
        self.nodes.append(node)

    def remove_node(self, *, node):
        self.nodes.remove(node)


app = FastAPI()
node_manager = NodeManager()


@app.get("/files/ls")
def get_files_ls():
    file_app = FileApp(workdir="./")

    result = dict()
    for node in node_manager.list_nodes():
        response = file_app.ls(target=node)
        result[node.agent_name] = response
    return result


@app.websocket("/v1/agents/{agent_id}")
async def handle_websocket(*, websocket: WebSocket, agent_id: str):

    await websocket.accept()

    node = rpc.Target(agent_name=agent_id, broker=rpc.broker.Broker())
    node_manager.add_node(node=node)

    try:

        async def send_worker(*, broker: rpc.broker.Broker, websocket: WebSocket):
            import queue

            async def get_async(q: queue.Queue):
                while True:
                    try:
                        item = q.get_nowait()
                        return item
                    except queue.Empty:
                        await asyncio.sleep(0.1)

            while True:
                msg = await get_async(broker.send_buffer)
                print(f"sent: {msg}")
                await websocket.send_text(msg)

        async def recv_worker(*, broker: rpc.broker.Broker, websocket: WebSocket):
            while True:
                msg = await websocket.receive_text()
                print(f"received: {msg}")
                broker.recv_buffer.put(msg)

        asyncio.create_task(send_worker(broker=node._broker, websocket=websocket))
        asyncio.create_task(recv_worker(broker=node._broker, websocket=websocket))

        while True:
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        node_manager.remove_node(node=node)
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app)
