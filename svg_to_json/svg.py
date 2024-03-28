from typing import Iterator
from xml.dom.minidom import Node, Element


def find_elements(node: Node, tag_name: str | None = None) -> Iterator[Element]:
    if isinstance(node, Element):
        if tag_name is None or node.tagName == tag_name:
            yield node
    for child in node.childNodes:
        yield from find_elements(child, tag_name)


def find_element_by_id(node: Node, id: str, tag_name: str | None = None) -> Element | None:
    for element in find_elements(node, tag_name):
        if element.getAttribute("id") == id:
            return element
    return None
