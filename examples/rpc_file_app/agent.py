import pathlib
import socket

from apps import FileApp

from gc_sdk import rpc

file_app = FileApp(workdir=pathlib.Path("./"))

agent_name = socket.gethostname()

agent = rpc.Agent(
    name=agent_name,
    broker=rpc.broker.WebsocketBroker(
        server="ws://localhost:8000/v1/agents", agent_name=agent_name
    ),
)
agent.register_app(file_app)


if __name__ == "__main__":
    try:
        thread = agent.start()
        thread.join()
    except Exception:
        raise
