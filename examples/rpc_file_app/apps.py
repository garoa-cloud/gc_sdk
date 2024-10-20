import pathlib

from gc_sdk import rpc


class FileApp:
    def __init__(self, workdir: pathlib.Path):
        self.workdir = workdir

    @rpc.remote_call
    def ls(self) -> list[str]:
        items = [p.name for p in self.workdir.iterdir()]
        return items
