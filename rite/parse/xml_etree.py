import html
from enum import Enum
from xml.etree.ElementTree import Element
from typing import List, Iterable, Dict, Optional, Type, Any

from rite.richtext import (
    BaseText, Join, String,
    Semantics, FontStyles, FontVariants, FontSizes, FontSize, Semantic,
    FontStyle, FontVariant, FontWeight
)


def unescape(value: str) -> str:
    return html.unescape(value)


def _enum_map(enum: Type[Enum]) -> Dict[str, Any]:
    return dict((x.value, x) for x in enum)


_semantics_map: Dict[str, Semantics] = _enum_map(Semantics)
_font_style_map: Dict[str, FontStyles] = _enum_map(FontStyles)
_font_variant_map: Dict[str, FontVariants] = _enum_map(FontVariants)
_font_size_map: Dict[str, FontSizes] = _enum_map(FontSizes)


def style_attrib(attrib: Dict[str, str], name: str) -> Optional[str]:
    parts = attrib.get("style", "").split(";")
    return dict(part.partition(':')[::2] for part in parts).get(name)


def element_font_size(element: Element) -> Optional[FontSizes]:
    size = style_attrib(element.attrib, "font-size")
    return _font_size_map.get(size) if size is not None else None


def element_font_style(element: Element) -> Optional[FontStyles]:
    style = style_attrib(element.attrib, "font-style")
    return (_font_style_map.get(style) if style is not None
            else (FontStyles.ITALIC if element.tag == 'i' else None))


def element_font_variant(element: Element) -> Optional[FontVariants]:
    variant = style_attrib(element.attrib, "font-variant")
    return _font_variant_map.get(variant) if variant is not None else None


def element_font_weight(element: Element) -> Optional[int]:
    weight = style_attrib(element.attrib, "font-weight")
    return (int(weight) if weight is not None
            else (700 if element.tag == 'b' else None))


def text_from_list(texts: List[BaseText]) -> BaseText:
    if len(texts) == 1:
        return texts[0]
    elif len(texts) > 1:
        return Join(texts)
    else:
        return String('')


def parse_xml_etree(element: Element) -> Iterable[BaseText]:
    # parse children
    children: List[BaseText] = []
    if element.text:
        children.append(String(unescape(element.text)))
    for sub_element in element:
        children.extend(parse_xml_etree(sub_element))
    # embed in rich style if need be
    semantic = _semantics_map.get(element.tag)
    if semantic is not None:
        children = [Semantic(text_from_list(children), semantic)]
    font_size = element_font_size(element)
    if font_size is not None:
        children = [FontSize(text_from_list(children), font_size)]
    font_style = element_font_style(element)
    if font_style is not None:
        children = [FontStyle(text_from_list(children), font_style)]
    font_variant = element_font_variant(element)
    if font_variant is not None:
        children = [FontVariant(text_from_list(children), font_variant)]
    font_weight = element_font_weight(element)
    if font_weight is not None:
        children = [FontWeight(text_from_list(children), font_weight)]
    yield from children
    # return the tail
    if element.tail:
        yield String(unescape(element.tail))
