import abc


class ParserInterface(abc.ABC):
    @abc.abstractmethod
    def encode(self, data): ...

    @abc.abstractmethod
    def decode(self, data): ...


class Logging(ParserInterface):
    def encode(self, data):
        print(f"sendinig {data}")
        return data

    def decode(self, data):
        print(f"receiving {data}")
        return data


class JSON(ParserInterface):
    def encode(self, data: dict | str):
        import json

        data = json.dumps(data)
        return data

    def decode(self, data: dict | str):
        import json

        data = json.loads(data)
        return data


class Encryption(ParserInterface):
    def encode(self, data: dict | str):
        return data

    def decode(self, data: dict | str):
        return data


class Signature(ParserInterface):
    def encode(self, data: dict | str):
        return data

    def decode(self, data: dict | str):
        return data
