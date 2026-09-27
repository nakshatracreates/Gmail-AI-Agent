from typing import TypedDict, Any


class EmailState(TypedDict):
    messages: list[Any]
    approved: bool | None