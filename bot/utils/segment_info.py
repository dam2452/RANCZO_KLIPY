

# fixme no z dupy troche: 1) serio mozesz miec wszystko None? 2) Uzywasz w projekcie jednoczesnie BytesIO i zwyklych bytes?
#fixme 1) z tym none to jest też zakręcony pierdolnik bo save miało się inaczej zachowywać w zależności czy ostatni klip to kompilacja czy zwykły czy rozszerzony itp
#i tam się te IFy warstwiły a teraz po tym jak gpt to ścisnął do tego structa pythonowego to gówno ożyło i wyszło z wroka XD
#fixme 2) no taka sytuacja bo myślałem żeby nie robić tmpfile tylko bytesio ale tmpfile zadziało od buta więc zmieniłem zdanie XD a w save to bytesIO zostało więc taka sytuacja XD
# a gpt jak to przefaktorował to widać mocniej ten pierdolniczek bo wcześniej się chował XD

#fixme poprawiłem to bytesIO ale bez zmiany bazy to nie wiele dałol bo dalej zamiast się odwałać to odstaniego filmiku z sesji w bazie się pierdolimy na jakiś kombinacjaach z jsonem w dictch itp
# trzeba by pp porządny wpis bo bazu zajebac gdzię będzie info o klipie i sam ten ostatni klip .mp4 w t BOLBie i on żeby pp wskakiwał na inna tabele jak ktoś go zapsiuje
#dlatego póki nie ma bazy imo szkoda się pierdolić z tym save i segment_info bo i tak całą obena logika pójdzie do cipy

from dataclasses import (
    dataclass,
    field,
)
from typing import Optional


@dataclass
class EpisodeInfo:
    season: Optional[int] = None
    episode_number: Optional[int] = None


@dataclass
class SegmentInfo:
    video_path: Optional[str] = None
    start: int = 0
    end: int = 0
    episode_info: EpisodeInfo = field(default_factory=EpisodeInfo)
    compiled_clip: Optional[bytes] = None
    expanded_clip: Optional[bytes] = None
    expanded_start: int = 0
    expanded_end: int = 0
