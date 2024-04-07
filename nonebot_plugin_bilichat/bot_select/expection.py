from typing import Any


class AdapterNotSupportedError(Exception):
    def __init__(self, adapter_name: str) -> None:
        message = f'adapter "{adapter_name}" not supported'
        super().__init__(self, message)


class NoBotFoundError(RuntimeError):
    def __init__(self, platform: Any) -> None:
        message = f'no bot found for "{platform}"'
        super().__init__(self, message)
