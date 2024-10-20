# Parsers


As connections between the agent and server are stateless, the pair call/response is not attached to an open socket like would be in a http requets, the standard way of implementing middleware was adapted to instead of keeping the callstack we have a sequence of parsers that implement the encode/decode interface.

```python
import abc

class ParserInterface(abc.ABC):
    @abc.abstractmethod
    def encode(self, data):
        ...

    @abc.abstractmethod
    def decode(self, data):
        ...
```



```python
from gc_sdk.rpc.parsers import Logging, JSON, Encryption, Signature

conn = Connection()

conn.use(Logging())
conn.use(JSON())
conn.use(Encryption())
conn.use(Signature())

conn.send('hi')
data = conn.receive()
```

```json
{
    "headers": {
        "parsers": ["JSON", "Encryption:AES-256", "Signature:SHA512"]
    }
}
```

## Logging

```python
class Logging(ParserInterface):
    def encode(self, data):
        print(f'sendinig {data}')
        return data

    def decode(self, data):
        print(f'receiving {data}')
        return data
```

## JSON
```python
class JSON(ParserInterface):
    def encode(self, data):
        return data

    def decode(self, data):
        data = json.loads(data)
        return data
```

## Encryption
```python
class Encryption(ParserInterface):
    def encode(self, data):
        return data

    def decode(self, data):
        return data
```

## Signature
```python
class Signature(ParserInterface):
    def encode(self, data):
        return data

    def decode(self, data):
        return data
```