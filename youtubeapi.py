#! /usr/bin/env python3

import json
from apiclient.discovery import build
import property

API_KEY = property.YOUTUBE_API_KEY
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

class YoutubeApi():

    def __init__(self):
        self.youtube = build(
            API_SERVICE_NAME,
            API_VERSION,
            developerKey = API_KEY
        )

    def search_live(self, channel_id):
        response = self.youtube.search().list(
            part = 'snippet',
            channelId = channel_id,
            type = 'channel'
        ).execute()
        return response


if __name__ == "__main__":
    api = YoutubeApi()
    res = api.search_live(input())
    # print(res)
    for item in res.get('items', []):
        print(json.dumps(item, indent=2, ensure_ascii=False))
    

