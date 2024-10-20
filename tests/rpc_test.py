from gc_sdk import rpc
from gc_sdk.rpc import broker


class MathApp:

    @rpc.remote_call
    def sum(self, a, b) -> int:
        return a + b


def test_call_remote_function():
    # setup app
    math_app = MathApp()

    # setup agent
    agent_a = rpc.Agent("region-a", broker=broker.Broker())
    agent_a.register_app(math_app)
    agent_a.start()

    # mock server
    target = rpc.Target(agent_name="region-a")
    target._broker.link(to=agent_a._broker)

    # call
    assert math_app.sum(target=target, a=3, b=5) == 8
