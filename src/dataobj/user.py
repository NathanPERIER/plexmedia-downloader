
from typing import Final, Mapping


class PlexUser :

    def __init__(self, data: Mapping[str, str]) :
        self.user_id:    Final[str] = data['id']
        self.uuid:       Final[str] = data['uuid']
        self.username:   Final[str] = data['username']
        self.email:      Final[str] = data['email']
        self.joined_at:  Final[str] = data['joined_at']
        self.auth_token: Final[str] = data['authToken']
