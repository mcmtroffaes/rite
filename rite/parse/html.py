from xml.etree.ElementTree import fromstring
from typing import Iterable

from rite.parse.xml_etree import parse_xml_etree
from rite.richtext import Text


def parse_html(source: str) -> Iterable[Text]:
    return parse_xml_etree(fromstring(f"<body>{source}</body>"))
