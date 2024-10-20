from . import parsers


def test_json():
    parser = parsers.JSON()
    message = {"message": "hello"}
    encoded = parser.encode(data=message)
    assert encoded == '{"message": "hello"}'

    decoded = parser.decode(data=encoded)
    assert decoded == message


def test_encryption(): ...


def test_signature(): ...
