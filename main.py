#!/usr/bin/python3

from src.constants            import BASE_HEADERS
from src.authenticator        import PlexAuthenticator
from src.dataobj.auth_data    import PlexAuthData
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

from typing import Sequence, Mapping, Tuple, Optional, Any


def parse_url(url: str) -> Tuple[str,str] :
    frag = urlparse(urlparse(url).fragment.lstrip('!'))
    params = parse_qs(frag.query)
    return (
        frag.path.split('/')[2],
        params['key'][0]
    )


class PlexDownloader:

    def _get_url(self, url) :
        response = requests.get(url, headers = {
            **BASE_HEADERS,
            'X-Plex-Token': self.server.access_token
        })

        if response.ok :
            return response.json()
        raise DownloadError(f"request to url \"{url}\" yielded response code {response.status_code} {response.reason}")

    def _parse_movie(self, movie): # TODO
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
            self._parse_movie(data)

        print(f"Media type {data['type']} isn't supported yet")
        return None

    def _get_metadata(self) -> Sequence[PlexNode] :
        response = self._get_url(self.server.uri + self.rating_key)
        return [
            self.parse_media(data)
            for data in response['MediaContainer']['Metadata']
        ]
    

    def download(self) :

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
                    print(f"Got HTTP {response.status_code} error while downloading {m.name}")
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

        self.original_filename = args.original_filename
        self.skip_existing = args.skip_existing

        auth_data = PlexAuthData()
        auth_data.username = args.username
        auth_data.password = args.password
        auth_data.token    = args.token
        auth_data.cookie   = args.cookie

        if args.authfile is not None and not auth_data.is_valid() :
            auth_data.load_file(args.authfile)
        
        server_hash, self.rating_key = parse_url(args.url)

        authenticator = PlexAuthenticator(auth_data)
        self.server = authenticator.get_server(server_hash)

        self.download()

    def __init__(self) :
        pass


if __name__ == "__main__":
    plex = PlexDownloader()
    plex.command_line()
