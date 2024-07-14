import json
from typing import (
    Dict,
    List,
    Union,
)

# fixme tam już wcześniej pisałem ale jeszcze tu napisze to można scalić do dwóch last_clip
# i last_search czy coś takiego i wjebać to do bazy tylko trzeba przy przechować info ze to coś ostatniego to np kompilacaj żeby nie szło jej roszserzać
# na razie se to odpuszcze to bo to trzeba mocniej przekiminić i może od razu pod baze załadować
# edit albo chuj trochę tego już teraz zredukowałem IDE ma takie kosmiczne opcje że kurła XD

# fixme zrob z tymi dictami co chcesz, na razie tego nie wyrzucaj w baze, niech to sie spina po prostu jako tako i patrz zeby sie importowalo xD to ty wiesz co one maja robic i do czego sa
last_selected_segment: Dict[int, json] = {}
last_search: Dict[int, Dict[str, List[json]]] = {}
last_clip: Dict[int, Dict[str, Union[json, str]]] = {}
