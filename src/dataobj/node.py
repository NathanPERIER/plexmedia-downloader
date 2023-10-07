
from .media_record import PlexMediaRecord

from abc import ABC, abstractmethod
from typing import Sequence

class PlexNode(ABC) :

    @abstractmethod
    def get_media(self, server_uri: str) -> Sequence[PlexMediaRecord] :
        pass

    @abstractmethod
    def get_name(self) -> str :
        pass

    @abstractmethod
    def get_base_name(self) -> str :
        pass
