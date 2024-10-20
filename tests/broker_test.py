import pytest

from gc_sdk.rpc import AsyncBroker, Broker


@pytest.fixture
def test_msg():
    return "just a test"


def test_broker_send_buffer(test_msg):
    broker = Broker()
    broker.send(test_msg)
    item = broker.send_buffer.get()
    assert item == test_msg


def test_broker_receive_buffer(test_msg):
    broker = Broker()
    broker.recv_buffer.put(test_msg)
    item = broker.recv()
    assert item == test_msg


def test_connect_sync_brokers():
    client_broker = Broker()
    server_broker = Broker()

    client_broker.link(to=server_broker)

    client_broker.send("hello")
    assert server_broker.recv() == "hello"

    server_broker.send("world")
    assert client_broker.recv() == "world"


@pytest.mark.asyncio
async def test_connect_async_brokers():
    client_broker = AsyncBroker()
    server_broker = AsyncBroker()

    client_broker.link(to=server_broker)

    await client_broker.send("hello")
    assert await server_broker.recv() == "hello"

    await server_broker.send("world")
    assert await client_broker.recv() == "world"


@pytest.mark.asyncio
async def test_connect_sync_to_async_brokers():
    client_broker = Broker()
    server_broker = AsyncBroker()

    client_broker.link(to=server_broker)

    client_broker.send("hello")
    assert await server_broker.recv() == "hello"

    await server_broker.send("world")
    assert client_broker.recv() == "world"
