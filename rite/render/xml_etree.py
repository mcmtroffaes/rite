import html

from functools import singledispatch
from typing import Iterable, Optional, List, Tuple
from xml.etree.ElementTree import Element

from rite.richtext import (
    BaseText, Join, Semantic, FontSize, FontStyle, FontVariant, FontWeight,
    Child, FontStyles
)
from rite.richtext.utils import iter_strings


def escape(value: str) -> str:
    return html.escape(value)


def text_style_property(text: Child) -> Optional[str]:
    if isinstance(text, FontSize):
        return f"font-size:{text.font_size.value}"
    elif isinstance(text, FontStyle):
        return f"font-style:{text.font_style.value}"
    elif isinstance(text, FontVariant):
        return f"font-variant:{text.font_variant.value}"
    elif isinstance(text, FontWeight):
        return f"font-weight:{text.font_weight}"
    return None


# generates a string sequence followed by one or more xml elements
# strings in between elements are in the "tail" attribute of each element
@singledispatch
def render_xml_etree(text: BaseText
                     ) -> Tuple[Optional[str], Iterable[Element]]:
    return ''.join(map(escape, iter_strings(text))), []


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


@render_xml_etree.register(Child)
def _child(text: Child) -> Tuple[Optional[str], Iterable[Element]]:
    element = Element(
        text.semantic.value if isinstance(text, Semantic) else "span")
    style_property = text_style_property(text)
    if style_property is not None:
        element.attrib["style"] = style_property
    element.text, children = render_xml_etree(text.child)
    element.extend(children)
    return None, [element]


@render_xml_etree.register(FontWeight)
def _font_weight(text: FontWeight) -> Tuple[Optional[str], Iterable[Element]]:
    if text.font_weight == 700:
        element = Element('b')
        element.text, children = render_xml_etree(text.child)
        element.extend(children)
        return None, [element]
    else:
        return _child(text)


@render_xml_etree.register(FontStyle)
def _font_style(text: FontStyle) -> Tuple[Optional[str], Iterable[Element]]:
    if text.font_style == FontStyles.ITALIC:
        element = Element('i')
        element.text, children = render_xml_etree(text.child)
        element.extend(children)
        return None, [element]
    else:
        return _child(text)
