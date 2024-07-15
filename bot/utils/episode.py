from typing import Optional, Tuple


class InvalidSeasonEpisodeStringException(Exception):
    def __init__(self, episode_string: str):
        self.message = f"Invalid season episode string '{episode_string}'"
        super().__init__(self.message)


class Episode:
    EPISODES_PER_SEASON: int = 13

    def __init__(self, season_episode: str) -> None:
        if season_episode[0] != "S" or season_episode[3] != "E":
            raise InvalidSeasonEpisodeStringException(season_episode)

        self.season: int = int(season_episode[1:3])
        self.number: int = int(season_episode[4:6])

    def get_absolute_episode_number(self) -> int:
        return (self.season - 1) * Episode.EPISODES_PER_SEASON + self.number


def adjust_episode_number(absolute_episode: int) -> Optional[Tuple[int, int]]:
    season = (absolute_episode - 1) // 13 + 1
    episode = (absolute_episode - 1) % 13 + 1
    return season, episode
