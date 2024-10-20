import json
import threading
from typing import Callable

from . import broker


class Agent:
    """
    Agent is an entity that exists both on the server and on the edge(localtion where we want the actions to be performed)
    In the server it will be responsable to dispatch calls to its counterpart in the edge, and on the edge it will be
    responsable to handle those calls and return the result back to the server.
    """

    def __init__(self, name: str, broker: broker.Broker) -> None:
        self.name = name
        self._handlers: dict[str, tuple[object, Callable]] = dict()

        self._broker = broker
        # else:
        #     protocol = server.split(":")[0]
        #     if protocol not in ["ws", "wss"]:
        #         raise ValueError(
        #             f"invalid server address. except something like ws://api.acme/agent but got: {server}"
        #         )

        #     server = f"{server}/{self.name}"
        #     self.broker = broker.WebsocketBroker(server)

    def register_handler(self, key: str, instance: object, handler: Callable):
        self._handlers[key] = (instance, handler)

    def register_app(self, app: object):
        def list_methods(cls: object):
            methods_list = [
                method
                for method in dir(cls)
                if callable(getattr(cls, method)) and not method.startswith("__")
            ]
            return methods_list

        app_name = app.__class__.__name__

        for method_name in list_methods(app):
            func_name = f"{app_name}:{method_name}"
            handler = getattr(app, method_name)
            self.register_handler(key=func_name, instance=app, handler=handler)

    def _request_worker(self):
        print("waiting requests")
        while True:
            payload = self._broker.recv()

            # TODO: add support to pydantic
            event = payload["event"]
            call_id = payload["call_id"]
            target = payload["target"]
            func_name = payload["func_name"]
            kwargs = payload["kwargs"]

            assert event == "call"
            assert target == self.name

            (instance, handler) = self._handlers[func_name]
            result = handler.exec(instance, **kwargs)

            result_message = {"call_id": call_id, "status": "done", "result": result}

            self._broker.send(result_message)
            print(f"result: {result_message}")

    def start(self) -> threading.Thread:
        """
        start a worker thread that will listen for events and call the respective handlers
        returns:
            thread(threading.Thread): worker thread
        """
        print(f"starting agent {self.name}")
        thread = threading.Thread(target=self._request_worker, daemon=True)
        thread.start()

        self._broker.sync()

        return thread
