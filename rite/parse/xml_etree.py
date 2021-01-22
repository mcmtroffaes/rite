import html
from xml.etree.ElementTree import Element
from typing import List, Iterable, Dict, Optional

from rite.richtext import (
    BaseText, Rich, Join, Semantics, String, Style, FontStyle
)


def unescape(value: str) -> str:
    return html.unescape(value)


semantics_map: Dict[str, Semantics] = dict(
    (tag.value, tag) for tag in Semantics)


def element_style(element: Element) -> Optional[Style]:
    style = Style(
        semantics=semantics_map.get(element.tag),
        font_weight=700 if element.tag == 'b' else 400,
        font_style=(
            FontStyle.ITALIC if element.tag == 'i' else FontStyle.NORMAL),
    )
    return style if style != Style() else None


def parse_xml_etree(element: Element) -> Iterable[BaseText]:
    # parse children
    children: List[BaseText] = []
    if element.text is not None:
        children.append(String(unescape(element.text)))
    for sub_element in element:
        children.extend(parse_xml_etree(sub_element))
    # embed in tag if need be
    style = element_style(element)
    if style is not None:
        if len(children) == 1:
            yield Rich(children[0], style)
        elif len(children) > 1:
            yield Rich(Join(children), style)
        else:
            yield Rich(String(''), style)
    else:
        yield from children
    if element.tail is not None:
        yield String(unescape(element.tail))
