import io
import re

import requests

from .exceptions import EmoteNotFoundException, InvalidCommandException


class Emote:
    def __init__(self, emote_type, emote_id, emote_channel):
        self.emote_type = emote_type
        self.emote_id = emote_id
        self.emote_channel = emote_channel
        self.name = self.get_name()
        self.image = self.get_image()

    def get_name(self):
        if self.emote_type == 'twitch':
            api_url = 'https://api.twitchemotes.com/api/v4/emotes'
            api_res = requests.get(api_url, params={'id': self.emote_id}).json()
            return api_res[0]['code']

        elif self.emote_type == 'ffz':
            api_url = f'https://api.frankerfacez.com/v1/emote/{self.emote_id}'
            api_res = requests.get(api_url).json()
            return api_res['emote']['name']

        elif self.emote_type == 'bttv':
            if self.emote_channel == 'global':
                api_url = 'https://api.betterttv.net/2/emotes'
            else:
                api_url = f'https://api.betterttv.net/2/channels/{self.emote_channel}'
            api_res = requests.get(api_url).json()
            for emote in api_res['emotes']:
                if emote['id'] == self.emote_id:
                    return emote['code']

    def get_image(self):
        img = None
        if self.emote_type == 'twitch':
            img = requests.get(f'https://static-cdn.jtvnw.net/emoticons/v1/{self.emote_id}/3.0').content
        elif self.emote_type == 'bttv':
            img = requests.get(f'https://cdn.betterttv.net/emote/{self.emote_id}/3x').content
        elif self.emote_type == 'ffz':
            img = requests.get(f'https://cdn.frankerfacez.com/emoticon/{self.emote_id}/4').content
        return io.BytesIO(img)

    @staticmethod
    def get_emote(cmd):
        cmd_re = re.compile(r'^\b(twitch|bttv|ffz)\b\s([\w\d]+)(?:\s(.+))?$', re.I | re.M)
        cmd_match = re.match(cmd_re, cmd)

        if not cmd_match:
            raise InvalidCommandException()

        emote_type = cmd_match[1].lower()
        emote_id = cmd_match[2].strip().lower()

        emote_channel = None
        if emote_type == 'bttv':
            emote_channel = cmd_match[3]
            if not emote_channel:
                raise InvalidCommandException()
            emote_channel = emote_channel.lower()

        try:
            emote = Emote(emote_type, emote_id, emote_channel)
            return emote
        except (KeyError, IndexError):
            raise EmoteNotFoundException()
