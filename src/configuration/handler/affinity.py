from typing import Optional

from pydantic import PlainSerializer, WithJsonSchema, BeforeValidator
from typing_extensions import Annotated

from util.cpu import parse_affinity, format_affinity


def __to_list(value) -> Optional[list[int]]:
    if isinstance(value, list):
        return value

    if not value.strip():
        return None

    return parse_affinity(value)


def __to_str(value) -> Optional[str]:
    if not value:
        return None

    if isinstance(value, list):
        return format_affinity(value)

    return value


Affinity = Annotated[
    Optional[list[int]],
    BeforeValidator(__to_list),
    PlainSerializer(__to_str, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization'),
]
