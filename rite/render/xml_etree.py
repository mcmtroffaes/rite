import html

from functools import singledispatch
from typing import Iterable, Optional, List, Tuple
from xml.etree.ElementTree import Element

from rite.richtext import BaseText, Tag, Join
from rite.richtext.utils import text_iter


def escape(value: str) -> str:
    return html.escape(value)


# generates a string sequence followed by one or more xml elements
# strings in between elements are in the "tail" attribute of each element
@singledispatch
def render_xml_etree(text: BaseText) -> Tuple[Optional[str], Iterable[Element]]:
    return ''.join(map(escape, text_iter(text))), []


@render_xml_etree.register(Tag)
def _tag(text: Tag) -> Tuple[Optional[str], Iterable[Element]]:
    element = Element(text.tag.value)
    element.text, children = render_xml_etree(text.text)
    element.extend(children)
    return None, [element]


@render_xml_etree.register(Join)
def _join(text: Join) -> Tuple[Optional[str], Iterable[Element]]:
    head_text: Optional[str] = None
    children: List[Element] = []
    for part in text.parts:
        part_text, part_children = render_xml_etree(part)
        if part_text:
            if children:
                last_element = children[-1]
                if last_element.tail is None:
                    last_element.tail = part_text
                else:
                    last_element.tail += part_text
            else:
                if head_text is None:
                    head_text = part_text
                else:
                    head_text += part_text
        children.extend(part_children)
    return head_text, children
