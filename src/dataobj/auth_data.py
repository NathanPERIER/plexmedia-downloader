
import json

from typing import Optional


class PlexAuthData :

    def __init__(self) :
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.token:    Optional[str] = None
        self.cookie:   Optional[str] = None
    
    def load_file(self, filepath: str) :
        with open(filepath, 'r') as f :
            auth_data = json.load(f)
        for field in ['username', 'password', 'token', 'cookie'] :
            if field in auth_data and type(auth_data[field]) == str :
                self.__dict__[field] = auth_data[field]
    
    def prompt_creds(self) :
        if self.username is None:
                self.username = input('Enter username > ')
        if self.password is None:
            from src.utils.getpass import getpass
            self.password = getpass('Enter password > ')
    
    def is_valid(self) -> bool :
        return (self.username is not None and self.password is not None) or self.token is not None or self.cookie is not None
    