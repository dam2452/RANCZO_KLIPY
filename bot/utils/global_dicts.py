import json
from typing import (
    Dict,
    List,
    Union,
)

last_selected_segment: Dict[int, json] = {}
last_search: Dict[int, Dict[str, List[json]]] = {}
last_clip: Dict[int, Dict[str, Union[json, str]]] = {}
