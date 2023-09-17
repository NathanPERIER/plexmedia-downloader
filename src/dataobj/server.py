
from typing import Final, Mapping, Any


class PlexServer :

    def __init__(self, data: Mapping[str, Any]) :
        self.name:           Final[str]  = data['name']
        self.client_id:      Final[str]  = data['clientIdentifier']
        self.access_token:   Final[str]  = data['accessToken']
        self.public_address: Final[str]  = data['publicAddress']
        self.online:         Final[bool] = data['presence']
        for conn in data['connections'] :
            if conn['address'] == self.public_address :
                self.uri: Final[str] = conn['uri']
                break
