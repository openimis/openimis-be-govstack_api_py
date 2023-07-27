from typing import Protocol


class BaseRegistry:

    class RegistryProtocol(Protocol):
        def get_record(self) -> None:
            ...

        def update_record(self) -> None:
            ...

        def delete_record(self) -> None:
            ...

        def check_if_record_exists(self) -> None:
            ...
