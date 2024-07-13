import json
from typing import (
    Dict,
    List,
)

last_selected_segment: Dict[int, json] = {}
last_search_quotes: Dict[int, List[json]] = {}
last_search_terms: Dict[int, str] = {}
last_compiled_clip: Dict[int, json] = {}
last_manual_clip: Dict[int, json] = {}
