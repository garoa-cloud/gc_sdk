import asyncio
import queue
import threading
import typing

from websockets.sync import client

from .parsers import JSON, Logging, ParserInterface




class Broker:
    def __init__(self):
        self.send_buffer = queue.Queue()
        self.recv_buffer = queue.Queue()
        self._parsers: list[ParserInterface] = [Logging(), JSON()]

    def _encode_data(self, data) -> str:
        for p in self._parsers:
            data = p.encode(data)
        return data

    def _decode_data(self, data: str) -> dict:
        for p in self._parsers:
            data = p.decode(data)
        return data

    def recv(self):
        data = self.recv_buffer.get()
        return self._decode_data(data)

    def send(self, data):
        data = self._encode_data(data)
        self.send_buffer.put(data)

    def link(self, *, to: typing.Self):
        self.send_buffer = to.recv_buffer
        self.recv_buffer = to.send_buffer

    def use(self, *, parser: ParserInterface):
        self._parsers.append(parser)
        
    def sync(self): ...


class AsyncBroker(Broker):

    async def recv(self):
        while True:
            try:
                data = self.recv_buffer.get_nowait()
                data = self._decode_data(data)
                return data

            except queue.Empty:
                await asyncio.sleep(0.1)

    async def send(self, data):
        data = self._encode_data(data)
        self.send_buffer.put(data)


class WebsocketBroker(Broker):
    def __init__(self, server, agent_name):
        super().__init__()
        self.uri = f"{server}/{agent_name}"

    def sync(self):
        websocket = client.connect(self.uri)

        def send_worker(websocket):
            try:
                while True:
                    data = self.send_buffer.get()
                    # data = self._encode_data(data)
                    websocket.send(data)
            except Exception as err:
                print(f"error: {err}")
                raise
            finally:
                websocket.close()

        def recv_worker(websocket):
            try:
                while True:
                    data = websocket.recv()
                    # data = self._decode_data(data)
                    self.recv_buffer.put(data)
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
