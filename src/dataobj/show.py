
from .episode      import PlexEpisode
from .node         import PlexNode
from .media_record import PlexMediaRecord

from typing import Final, Mapping, Sequence, Any


class PlexShow(PlexNode) :

    def __init__(self, data: Mapping[str, Any]) :
        assert data['viewGroup'] == 'episode'
        self.title:    Final[str] = data['parentTitle']
        self.year:     Final[str] = data['parentYear']
        self.episodes: Final[Sequence[PlexEpisode]] = [
            PlexEpisode(ep) for ep in data['Metadata']
        ]
        self.episodes.sort()
    
    def get_media(self, server_uri: str) -> Sequence[PlexMediaRecord] :
        res = []
        for ep in self.episodes :
            res.extend(ep.get_media(server_uri))
        return res

    def get_name(self) -> str :
        return self.title

    def get_base_name(self) -> str :
        return self.title


# 'MediaContainer'
