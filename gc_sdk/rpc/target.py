import json
import uuid
from typing import Optional

from gc_sdk.rpc import exceptions
from gc_sdk.rpc.broker import Broker


class Target:
    def __init__(
        self,
        *,
        agent_name: str,
        broker: Optional[Broker] = None,
    ):
        self.agent_name = agent_name
        if broker is None:
            self._broker = Broker()
        else:
            self._broker = broker

        self._call_stack = dict()

    def dispatch_call(self, func_name: str, kwargs: dict) -> str:
        call_id = str(uuid.uuid4())
        job = {
            "event": "call",
            "call_id": call_id,
            "target": self.agent_name,
            "func_name": func_name,
            "kwargs": kwargs,
        }
        self._broker.send(job)
        self._call_stack[call_id] = None

        return call_id

    def wait_result(self, call_id: str, timeout=5):
        """
        wait for a function be executed given the call_id.
        if the function did not return anything raises TimeoutError
        args:
            call_id(str): call identifier
            timeout(int): timeout in seconds
        """
        import threading
        import time
        from datetime import datetime, timedelta

        def sync():
            while True:
                item = self._broker.recv()
                call_id = item["call_id"]
                self._call_stack[call_id] = item

        threading.Thread(target=sync, daemon=True).start()

        started_at = datetime.now()
        while True:
            if (datetime.now() - started_at) > timedelta(seconds=timeout):
                raise exceptions.TimeoutError(f"timeout of {timeout} seconds reached")

            response = self._call_stack[call_id]
            if response is None:
                time.sleep(0.1)
                continue
            return response["result"]
