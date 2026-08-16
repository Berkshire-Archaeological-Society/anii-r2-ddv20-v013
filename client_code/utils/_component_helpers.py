import anvil.server
from anvil import Component as _Component

def _walker(children):
    for child in children:
        yield child
        get_children = getattr(child, "get_components", None)
        if get_children is not None:
            yield from _walker(get_children())


def walk(component_or_components):
    """yields the component(s) passed in and all their children"""
    if isinstance(component_or_components, _Component):
        component_or_components = [component_or_components]
    yield from _walker(component_or_components)



