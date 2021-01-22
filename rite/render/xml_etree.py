import html

from functools import singledispatch
from typing import Iterable, Optional, List, Tuple
from xml.etree.ElementTree import Element

from rite.richtext import (
    BaseText, Rich, Join, FontStyle, Style, Color, FontVariant
)
from rite.richtext.utils import text_iter


def escape(value: str) -> str:
    return html.escape(value)


# generates a string sequence followed by one or more xml elements
# strings in between elements are in the "tail" attribute of each element
@singledispatch
def render_xml_etree(text: BaseText
                     ) -> Tuple[Optional[str], Iterable[Element]]:
    return ''.join(map(escape, text_iter(text))), []


def color_property(color: Color) -> str:
    return f"rgb({color.r}, {color.g}, {color.b})"


def style_properties(style: Style) -> Tuple[str, str]:
    tag: str = 'span' if style.semantics is None else style.semantics.value
    properties: List[str] = []
    if style.font_style != FontStyle.NORMAL:
        if tag == 'span' and style.font_style == FontStyle.ITALIC:
            tag = 'i'
        else:
            properties.append(f"font-style:{style.font_style.value}")
    if style.font_weight != 400:
        if tag == 'span' and style.font_weight == 700:
            tag = 'b'
        else:
            properties.append(f"font-weight:{style.font_weight}")
    if style.color:
        properties.append(f"color:{color_property(style.color)}")
    if style.background_color:
        properties.append(
            f"background-color:{color_property(style.background_color)}")
    if style.font_variant != FontVariant.NORMAL:
        properties.append(f"font-variant:{style.font_variant.value}")
    if style.font_family is not None:
        properties.append(f"font-family:{style.font_family}")
    return tag, ';'.join(properties)


@render_xml_etree.register(Rich)
def _rich(text: Rich) -> Tuple[Optional[str], Iterable[Element]]:
    tag, properties = style_properties(text.style)
    element = Element(tag)
    element.text, children = render_xml_etree(text.child)
    element.extend(children)
    if properties:
        element.attrib["style"] = properties
    return None, [element]


@render_xml_etree.register(Join)
def _join(text: Join) -> Tuple[Optional[str], Iterable[Element]]:
    head_text: Optional[str] = None
    children: List[Element] = []
    for child in text.children:
        child_text, child_children = render_xml_etree(child)
        if child_text:
            if children:
                last_element = children[-1]
                if last_element.tail is None:
                    last_element.tail = child_text
                else:
                    last_element.tail += child_text
            else:
                if head_text is None:
                    head_text = child_text
                else:
                    head_text += child_text
        children.extend(child_children)
    return head_text, children
