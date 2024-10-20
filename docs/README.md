# WSS-RPC

This library can be used to build federated systems, or systems for configuration management.
The agent connects to the server, and the server call functions
that will be executed by the agent. In this format where the agent
is the entity that initiates the connection, it can connects even being behind
a firewall.




## How to use?

1. Define an **application**:

    To define an app we create a class, and add the decorator `@rpc.remote_procedure`
    to the methods that will be available to be remotely called.

    ```python
    # apps.py
    from gc_sdk import rpc
    class FileApp:
        @rpc.remote_procedure
        def ls(self):...
    ```

    The parameters of the function must be keword defined such as:
    ```python

    class FileApp:
        @rpc.remote_procedure
        def mkdir(self, *, dir_name: str):...
    ```

    Both parameters and return values must be JSON serializable.


2. Attach the application an **agent**:
    ```python
    # agent.py
    from gc_sdk import rpc
    from apps import FileApp

    file_app = FileApp()

    agent = rpc.Agent(server = 'wss://api.garoa.cloud/v1/agents/')
    agent.register_app(file_app)
    if __name__ == '__main__':
        agent.start()
    ```

    The agent will be responsable for connecting to the server and to route requests
    to an specific app.

3. Send requests to the agent

    We are ommiting the server code that handle the incomming requests, and register the agent
    as an available target. In the example bellow we have access to the list of connected targets 
    from `dc.list_nodes()`.

    The decorator `@rpc.remote_procedure` modified the method `ls()`, adding a new parameter `target`, so we have `ls(target)`
    ```python
    # client.py
    from gc_sdk import rpc
    from apps import FileApp

    app = FileApp()
    for node in dc.list_nodes():
        app.ls(target=node)

    ```

## How the server handle the requests?

