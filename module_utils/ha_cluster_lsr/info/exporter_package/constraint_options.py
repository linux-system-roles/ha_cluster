from typing import Any, List, Tuple, Union

from .wrap_src import SrcDict


def simple_options(
    src: SrcDict, *name_list: Union[str, Tuple[str, str]]
) -> List[Any]:
    """Takes options by name_list from src and returns them in role's format."""
    options = []
    for n in name_list:
        key, name = n if isinstance(n, tuple) else (n, n)
        if key in src and src[key]:
            options.append({"name": name, "value": src[key]})

    return options
