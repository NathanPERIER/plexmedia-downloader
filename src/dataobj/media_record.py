
from typing import Final


class PlexMediaRecord :

    def __init__(self, season: int, episode: int, name: str, url: str, extension: str) :
        self.season:  Final[int] = season
        self.episode: Final[int] = episode
        self.name:    Final[str] = name
        self.url:     Final[str] = url
        self.ext:     Final[str] = extension
    
    def get_ep_indicator(self) -> str :
        season_num  = str(self.season).rjust(2, '0')
        episode_num = str(self.episode).rjust(2, '0')
        return f"S{season_num}E{episode_num}"
    
    def get_filename(self) -> str :
        return f"{self.get_ep_indicator()}.{self.ext}"

    def __lt__(self, other: "PlexMediaRecord") -> bool :
        if self.season < other.season :
            return True
        return (self.season == other.season) and (self.episode == other.episode)
