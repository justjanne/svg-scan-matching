from svgelements import Viewbox

def patch_viewbox():
    def viewbox_transform(*args, **kwargs) -> str:
        return ""

    Viewbox.viewbox_transform = viewbox_transform