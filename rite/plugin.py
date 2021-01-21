import pkg_resources
from typing import Any


def find_plugin(group: str, name: str) -> Any:
    """Load a rite plugin."""
    dist = pkg_resources.get_distribution('rite')
    if group not in dist.get_entry_map():
        raise ImportError(f"plugin group {group} not found")
    for entry_point in pkg_resources.iter_entry_points(group, name):
        return entry_point.load()
    raise ImportError(f"plugin {group}.{name} not found")
