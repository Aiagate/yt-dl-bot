#! /usr/bin/env python3

from pytchat import LiveChat
import time
import numpy
import sqlite3
import shutil

from db_connect import DatabaseConnect
from utils import (
    OverlappingError
)
import property

class ChatViewModule():
    def __init__(self):
        pass

    def get_peaktime(self):
        pass

    def count_chatpeak(self, video_id):
        chat = LiveChat(video_id=video_id)
        db_name = 'databases/chatdata_' + video_id + '.db' 

        with DatabaseConnect(db_name=db_name) as db:
            try:
                db.execute('create table if not exists chatdata ' + property.CHAT_DATALIST)
            except Exception as e:
                raise e

        while chat.is_alive():
            try:
                data = chat.get()
                items = data.items
                for c in items:
                    print(f"{c.datetime} {c.timestamp} [{c.author.name}]- {c.message}")
                    # print(type(c.author.name))
                    with DatabaseConnect(db_name=db_name) as db:
                        try:
                            sql = 'insert into chatdata values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                            result = db.execute(sql,
                                c.id,
                                c.author.name,
                                c.author.channelId,
                                c.type,
                                c.message,
                                c.timestamp,
                                c.datetime,
                                c.amountValue,
                                c.amountString,
                                c.currency,
                                c.author.isVerified,
                                c.author.isChatOwner,
                                c.author.isChatSponsor,
                                c.author.isChatModerator
                            )
                        except Exception as e:
                            raise e
                time.sleep(3)
            except KeyboardInterrupt:
                chat.terminate()
                break
            except Exception as e:
                chat.terminate()
                raise e

if __name__ == '__main__':
    chatviewer = ChatViewModule()
    chatviewer.count_chatpeak('OqkDihODc2A')


