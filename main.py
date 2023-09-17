#!/usr/bin/python3

from src.dataobj.user         import PlexUser
from src.dataobj.server       import PlexServer
from src.dataobj.node         import PlexNode
from src.dataobj.show         import PlexShow
from src.dataobj.season       import PlexSeason
from src.dataobj.episode      import PlexEpisode
from src.dataobj.media_record import PlexMediaRecord
from src.utils.errors         import DownloadError
from src.utils.table          import TableBuilder

import requests
from urllib.parse import urlparse, parse_qs
from tqdm.auto import tqdm
import os
import argparse
import base64
import json

from typing import Sequence, Mapping, MutableMapping, Optional, Any


class PlexDownloader:
    headers = {
        'X-Plex-Client-Identifier': 'PlexDownloader',
        'X-Plex-Product': 'PlexDownloader',
        'Accept': 'application/json'
    }

    servers: MutableMapping[str, PlexServer] = {}

    def login(self):
        if self.cookie is not None:
            cookie = str(base64.b64decode(self.cookie), "utf-8")
            self.token = json.loads(cookie)["token"]

        if self.token:
            # Get user info
            headers = {
                **self.headers,
                'X-Plex-Token': self.token
            }

            r = requests.get("https://plex.tv/users/account.json", headers=headers)
        else:
            # Login
            payload = {
                'user[login]': self.email,
                'user[password]': self.password
            }

            r = requests.post("https://plex.tv/users/sign_in.json",
                              headers=self.headers, data=payload)

        if not r.ok :
            print(r.json()['error'])
            quit(1)

        self.user = PlexUser(r.json()['user'])

        return self.user

    def get_servers(self):
        # get servers
        headers = {
            **self.headers,
            'X-Plex-Token': self.user.auth_token
        }

        r = requests.get(
            "https://plex.tv/api/v2/resources?includeHttps=1&includeRelay=1", headers=headers)

        for server_data in r.json():
            server = PlexServer(server_data)
            self.servers[server.client_id] = server
        return self.servers

    def _get_url(self, url):
        headers = {
            **self.headers,
            'X-Plex-Token': self.server.access_token
        }

        response = requests.get(url, headers=headers)

        if response.ok :
            return response.json()
        raise DownloadError(f"request to url \"{url}\" yielded response code {response.status_code} {response.reason}")

    def _parse_movie(self, movie):
        key = movie["Media"][0]['Part'][0]['key']
        extension = key.split(".")[-1]

        if self.original_filename:
            filename = movie['Media'][0]['Part'][0]["file"].split("/")[-1]
        else:
            filename = movie['title'] + "." + extension

        folder = movie['title']

        return [
            {
                "url": self.server.uri + key,
                "filename": filename,
                "folder": folder,
                "title": movie['title']
            }
        ]

    def parse_media(self, data: Mapping[str, Any]) -> Optional[PlexNode]:
        if data['type'] == 'show' :
            url = self.server.uri + "/library/metadata/" + data['ratingKey'] + "/allLeaves"
            response = self._get_url(url)
            return PlexShow(response['MediaContainer'])

        elif data['type'] == 'season' :
            url = self.server.uri + "/library/metadata/" + data['ratingKey'] + "/children"
            response = self._get_url(url)
            return PlexSeason(response['MediaContainer'])

        elif data['type'] == 'episode' :
            return PlexEpisode(data)

        elif data['type'] == 'movie' :
            print(data)
            self._parse_movie(data) # TODO

        print(f"Media type {data['type']} isn't supported yet")
        return None
    

    def _parse_url(self, url: str):
        frag = urlparse(urlparse(url).fragment.lstrip('!'))
        params = parse_qs(frag.query)
        self.server_hash = frag.path.split('/')[2]
        self.rating_key = params['key'][0]

    def _get_metadata(self) -> Sequence[PlexNode] :
        response = self._get_url(self.server.uri + self.rating_key)
        return [
            self.parse_media(data)
            for data in response['MediaContainer']['Metadata']
        ]
    

    def download(self, url: str):
        self._parse_url(url)

        user = self.login()

        print(f"Logged in as {user.username}")

        servers = self.get_servers()
        server_count = len(servers)
        print(f"Found {server_count} server{'s' if server_count != 1 else ''}")

        if self.server_hash not in self.servers :
            raise DownloadError(f"user {user.username} doesn't have access to the server on which the resource is hosted")
        self.server = self.servers[self.server_hash]
        print(f"Downloading from Plex server at {self.server.name}")
        if not self.server.online :
            print('Caution: server may be offline')

        nodes = self._get_metadata()
        if len(nodes) == 0 :
            print('No media found')
            return
        
        headers = {
            'X-Plex-Token': self.server.access_token
        }

        for node in nodes :
            print(f"Found resource {node.get_name()}")

            folder_path = node.get_name().replace('/', '∕')
            if not os.path.exists(folder_path) :
                os.mkdir(folder_path)

            to_download: list[PlexMediaRecord] = []
            
            builder = TableBuilder(['Episode', 'Title', 'Download'], node.get_name())
            for m in node.get_media(self.server.uri) :
                skip = self.skip_existing and os.path.exists(os.path.join(folder_path, m.get_ep_indicator()))
                if not skip :
                    to_download.append(m)
                builder.add_row([m.get_ep_indicator(), m.name, 'no' if skip else 'yes'])
            builder.print()

            for m in to_download :
                response = requests.get(m.url, stream=True, headers=headers)
                if not response.ok :
                    print(f"Error HTTP {response.status_code} getting {m.name}")
                    continue

                file_name = os.path.join(folder_path, m.get_ep_indicator())
                with open(file_name, 'wb') as fout:
                    with tqdm(
                        unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                        desc=file_name, total=int(response.headers.get('content-length', 0))
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=4096):
                            fout.write(chunk)
                            pbar.update(len(chunk))


    def command_line(self):
        ap = argparse.ArgumentParser()

        ap.add_argument("-u", "--username", required=False, help="Plex.TV Email/Username")

        ap.add_argument("-p", "--password", required=False, help="Plex.TV Password")

        ap.add_argument("-c", "--cookie", required=False, help="Plex.tv Auth Sync cookie")

        ap.add_argument("-t", "--token", required=False, help="Plex Token")

        ap.add_argument("-f", "--authfile", required=False, help="Path to a json file containing authentication data")

        ap.add_argument("--original-filename", required=False,
                        default=False, action='store_true', help="Name content by original name")
        
        ap.add_argument("--skip-existing", required=False,
                        default=False, action='store_true', help="Skip files that already exist on the filesystem")
        
        # TODO
        # ap.add_argument("--cherrypick", required=False,
        #                 default=False, action='store_true', help="Hand pick which media to download")

        ap.add_argument("url", help="URL to Movie, Show, Season, Episode. TIP: Put url inside single quotes.")

        args = ap.parse_args()

        self.email = args.username
        self.password = args.password
        self.token = args.token
        self.cookie = args.cookie
        self.original_filename = args.original_filename
        self.skip_existing = args.skip_existing

        if args.authfile is not None and self.cant_authenticate_user() :
            with open(args.authfile, 'r') as f :
                auth_data = json.load(f)
            for field in ['email', 'password', 'token', 'cookie'] :
                if field in auth_data and type(auth_data[field]) == str :
                    self.__dict__[field] = auth_data[field]

        if self.cant_authenticate_user():
            if self.email is None:
                self.email = input('Enter username > ')
            if self.password is None:
                from src.utils.getpass import getpass
                self.password = getpass('Enter password > ')

        self.download(args.url)
    
    def cant_authenticate_user(self) :
        return ((self.email is None or self.password is None) and self.token is None and self.cookie is None)

    def __init__(self) :
        pass


if __name__ == "__main__":
    plex = PlexDownloader()
    plex.command_line()
