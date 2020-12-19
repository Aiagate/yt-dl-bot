#! /usr/bin/env python3
class YoutubeModuleError(Exception):
    pass

class OverlappingError(YoutubeModuleError):
    def __init__(self, msg):
        super(OverlappingError, self).__init__(msg)
        self.msg = msg