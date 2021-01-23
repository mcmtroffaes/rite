import sys
from typing import TypeVar, Iterable
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import Text


SourceType = TypeVar('SourceType', contravariant=True)


class ParseProtocol(Protocol[SourceType]):
    def __call__(self, source: SourceType) -> Iterable[Text]:
        pass  # pragma: no cover
