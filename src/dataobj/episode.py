
from typing import Final, Sequence, Mapping, Any

from .node         import PlexNode
from .media_record import PlexMediaRecord

from src.utils.format import format_ep_indicator


class PlexEpisode(PlexNode) :

    def __init__(self, data: Mapping[str, Any]) :
        self.key:      Final[str] = data['Media'][0]['Part'][0]['key']
        self.ext:      Final[str] = data['Media'][0]['container']
        self.show:     Final[str] = data['grandparentTitle']
        self.season:   Final[str] = data['parentIndex']
        self.episode:  Final[str] = data['index']
        self.title:    Final[str] = data['title']
        self.original_filename: Final[str] = data['Media'][0]['Part'][0]['file'].split('/')[-1]

    def get_media(self, server_uri: str) -> Sequence[PlexMediaRecord] :
        return [PlexMediaRecord(self.season, self.episode, self.title, server_uri + self.key, self.ext)]


    def get_base_name(self) -> str :
        return self.show

    def get_name(self) -> str :
        return f"{self.show} {format_ep_indicator(self.season, self.episode)}"
    
    def __lt__(self, other: "PlexEpisode") :
        if self.season < other.season :
            return True
        return (self.season == other.season) and (self.episode < other.episode)
