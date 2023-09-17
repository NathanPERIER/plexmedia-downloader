
import json
import base64
import requests

from .constants         import BASE_HEADERS
from .dataobj.auth_data import PlexAuthData
from .dataobj.user      import PlexUser
from .dataobj.server    import PlexServer
from .utils.errors      import DownloadError

from typing import Optional


class PlexAuthenticator :

    def __init__(self, auth_data: PlexAuthData) :
        if not auth_data.is_valid() :
            auth_data.prompt_creds()
        self.auth_data = auth_data
        self.user: Optional[PlexUser] = None
    

    def login(self) -> PlexUser :
        if self.user is not None :
            return self.user
        
        token = self.auth_data.token
        if self.auth_data.cookie is not None:
            cookie = str(base64.b64decode(self.auth_data.cookie), 'utf-8')
            token = json.loads(cookie)['token']

        if token is not None :
            r = requests.get("https://plex.tv/users/account.json", headers = {
                **BASE_HEADERS,
                'X-Plex-Token': token
            })
        else :
            r = requests.post("https://plex.tv/users/sign_in.json", headers=BASE_HEADERS, data = {
                'user[login]':    self.auth_data.username,
                'user[password]': self.auth_data.password
            })

        if not r.ok :
            raise DownloadError(f"User authentication error : {r.json()['error']}")

        self.user = PlexUser(r.json()['user'])
        print(f"Authenticated as {self.user.username}")

        return self.user
    
    
    def get_server(self, server_hash: str) -> PlexServer :
        user = self.login()
        r = requests.get("https://plex.tv/api/v2/resources?includeHttps=1&includeRelay=1", headers = {
            **BASE_HEADERS,
            'X-Plex-Token': user.auth_token
        })

        for server_data in r.json() :
            server = PlexServer(server_data)
            if server.client_id == server_hash :
                return server
        
        raise DownloadError(f"user {user.username} doesn't have access to the server on which the resource is hosted")

