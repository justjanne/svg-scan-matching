from typing import NamedTuple
from xml.dom.minidom import Node, Element


class DocumentMetrics(NamedTuple):
    view_box: str
    width: str | None
    height: str | None

    @staticmethod
    def of(node: Node):
        if isinstance(node, Element):
            if node.tagName == "svg":
                view_box = node.getAttribute("viewBox")
                width = node.getAttribute("width")
                height = node.getAttribute("height")
                return DocumentMetrics(view_box, width, height)
        for child in node.childNodes:
            result = DocumentMetrics.of(child)
            if result is not None:
                return result
