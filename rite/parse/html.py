from xml.etree.ElementTree import fromstring
from typing import Iterable

from rite.parse.xml import ParseXml
from rite.richtext import Text


class ParseHtml:
    def __call__(self, source: str) -> Iterable[Text]:
        return ParseXml()(fromstring(f"<body>{source}</body>"))
