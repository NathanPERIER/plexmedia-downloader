
from typing import Optional


class PlexAuthData :

    def __init__(self) :
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.token:    Optional[str] = None
        self.cookie:   Optional[str] = None
    
    def is_valid(self) -> bool :
        return (self.username is not None and self.password is not None) or self.token is not None or self.cookie is not None
    