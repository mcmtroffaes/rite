import html
from enum import Enum
from xml.etree.ElementTree import Element
from typing import List, Iterable, Dict, Optional, Type, Any

from rite.richtext import (
    BaseText, Rich, Join, String, Style,
    Semantics, FontStyle, FontVariant, FontSize
)


def unescape(value: str) -> str:
    return html.unescape(value)


def _enum_map(enum: Type[Enum]) -> Dict[str, Any]:
    return dict((x.value, x) for x in enum)


_semantics_map: Dict[str, Semantics] = _enum_map(Semantics)
_font_style_map: Dict[str, FontStyle] = _enum_map(FontStyle)
_font_variant_map: Dict[str, FontVariant] = _enum_map(FontVariant)
_font_size_map: Dict[str, FontSize] = _enum_map(FontSize)


def element_style(element: Element) -> Optional[Style]:
    semantics: Optional[Semantics] = _semantics_map.get(element.tag)
    font_style: FontStyle = \
        FontStyle.ITALIC if element.tag == 'i' else FontStyle.NORMAL
    font_weight: int = 700 if element.tag == 'b' else 400
    font_variant: FontVariant = FontVariant.NORMAL
    font_size: FontSize = FontSize.MEDIUM
    for prop in element.attrib.get("style", "").split(";"):
        prop_name, _, prop_value = prop.partition(":")
        if prop_name == "font-weight":
            font_weight = int(prop_value)
        elif prop_name == "font-style":
            font_style = _font_style_map.get(prop_value, FontStyle.NORMAL)
        elif prop_name == "font-variant":
            font_variant = _font_variant_map.get(
                prop_value, FontVariant.NORMAL)
        elif prop_name == "font-size":
            font_size = _font_size_map.get(prop_value, FontSize.MEDIUM)
    style = Style(
        semantics=semantics,
        font_weight=font_weight,
        font_style=font_style,
        font_variant=font_variant,
        font_size=font_size,
    )
    return style if style != Style() else None


def parse_xml_etree(element: Element) -> Iterable[BaseText]:
    # parse children
    children: List[BaseText] = []
    if element.text:
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
    if element.tail:
        yield String(unescape(element.tail))
