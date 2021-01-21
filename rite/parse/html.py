import html
from xml.etree.ElementTree import fromstring, Element
from typing import List, Iterable, Dict

from rite.richtext import BaseText, Tag, Join, TagType, String


def unescape(value: str) -> str:
    return html.unescape(value)


tag_map: Dict[str, TagType] = dict((tag.value, tag) for tag in TagType)


def parse_html(source: str) -> Iterable[BaseText]:
    return parse_xml_element(fromstring(f"<html>{source}</html>"))


def parse_xml_element(element: Element) -> Iterable[BaseText]:
    # parse children
    children: List[BaseText] = []
    if element.text is not None:
        children.append(String(unescape(element.text)))
    for sub_element in element:
        children.extend(parse_xml_element(sub_element))
    # embed in tag if need be
    tag_type = tag_map.get(element.tag)
    if tag_type is not None:
        text: BaseText
        if len(children) == 1:
            text = children[0]
        elif len(children) > 1:
            text = Join(children)
        else:
            text = String('')
        yield Tag(tag_type, text)
    else:
        yield from children
    if element.tail is not None:
        yield String(unescape(element.tail))
