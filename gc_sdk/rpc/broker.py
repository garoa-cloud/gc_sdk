import asyncio
import queue
import threading
import typing

from websockets.sync import client


class Broker:
    def __init__(self):
        self.send_buffer = queue.Queue()
        self.recv_buffer = queue.Queue()

    def recv(self):
        return self.recv_buffer.get()

    def send(self, item):
        self.send_buffer.put(item)

    def link(self, *, to: typing.Self):
        self.send_buffer = to.recv_buffer
        self.recv_buffer = to.send_buffer

    def sync(self): ...


class AsyncBroker(Broker):

    async def recv(self):
        while True:
            try:
                item = self.recv_buffer.get_nowait()
                return item

            except queue.Empty:
                await asyncio.sleep(0.1)

    async def send(self, item):
        self.send_buffer.put(item)


class WebsocketBroker(Broker):
    def __init__(self, server, agent_name):
        super().__init__()
        self.uri = f"{server}/{agent_name}"

    def sync(self):
        websocket = client.connect(self.uri)

        def send_worker(websocket):
            try:
                while True:
                    msg = self.send_buffer.get()
                    websocket.send(msg)
            except Exception as err:
                print(f"error: {err}")
                raise
            finally:
                websocket.close()

        def recv_worker(websocket):
            try:
                while True:
                    msg = websocket.recv()
                    self.recv_buffer.put(msg)
            except Exception as err:
                print(f"error: {err}")
                raise
            finally:
                websocket.close()

        threads = [
            threading.Thread(target=send_worker, daemon=True, args=(websocket,)),
            threading.Thread(target=recv_worker, daemon=True, args=(websocket,)),
        ]

        for t in threads:
            t.start()
