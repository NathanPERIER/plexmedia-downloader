
from .episode      import PlexEpisode
from .node         import PlexNode
from .media_record import PlexMediaRecord

from typing import Final, Mapping, Sequence, Any


class PlexSeason(PlexNode) :

    def __init__(self, data: Mapping[str, Any]) :
        assert data['viewGroup'] == 'episode'
        self.show:     Final[str] = data['grandparentTitle']
        self.number:   Final[int] = data['parentIndex']
        self.episodes: Final[Sequence[PlexEpisode]] = [
            PlexEpisode(ep) for ep in data['Metadata']
        ]
    
    def get_media(self, server_uri: str) -> Sequence[PlexMediaRecord] :
        res = []
        for ep in self.episodes :
            res.extend(ep.get_media(server_uri))
        return res

    def get_name(self) -> str :
        return f"{self.show} Season {self.number}"
    
    def get_base_name(self) -> str :
        return self.show
