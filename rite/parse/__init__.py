import sys
from typing import TypeVar, Iterable
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import BaseText


SourceType = TypeVar('SourceType', contravariant=True)


class ParseProtocol(Protocol[SourceType]):
    def __call__(self, source: SourceType) -> Iterable[BaseText]:
        pass  # pragma: no cover
