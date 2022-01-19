#! ./.venv/bin/python
# -*- coding: utf-8 -*-

# ---standard library---
import datetime
import logging
from logging import getLogger
import time

# ---third party library---
from pytchat import create

# ---local library---
from sql_connect import DatabaseConnect
import youtubeapi
import property


class ChatDataExtractor():
    def __init__(self):
        self.logger = getLogger(__name__)
        self.date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
        self.table_name = 'chat_data_whitetails'
    
    def search_video_keyword(self, keyword):
        with DatabaseConnect('youtube_chat') as db:
            try:
                db.cursor.execute(f'SELECT video_id FROM {self.table_name} where message like \"%{keyword}%\" group by video_id order by datetime;')
                result = db.cursor.fetchall()
            except Exception as e:
                raise e
        video_ids = []
        for video_id in result:
            video_ids.append(video_id)
        return video_ids

    def extract_from_keyword(self, video_id, keyword):
        with DatabaseConnect('youtube_chat') as db:
            try:
                # self.logger.debug(f'drop table if exists {self.table_name}')
                # db.cursor.execute(f'DROP TABLE IF EXISTS {self.table_name}')
                
                db.cursor.execute(f'SELECT elapsedTime FROM {self.table_name} where video_id = \"{video_id}\" AND message like \"%{keyword}%\" order by elapsedTime;')
                result = db.cursor.fetchall()
            except Exception as e:
                raise e
        time = 0
        search_result = []
        for elapsedTime in result:
            t = int(elapsedTime[0])
            t = t - 30
            if (t < time):
                continue
            url = f'https://youtu.be/{video_id}'
            search_result.append(f'{url}?t={t}')
            time = t + 100
        return search_result
        
    

if __name__ == '__main__':
    import logging
    from logging import DEBUG, INFO, Logger, getLogger
    logging.basicConfig(
        level=INFO,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-24s %(funcName)-16s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    fh = logging.FileHandler(filename='log/chat_data_search_system.log', encoding='utf-8')
    fh.setLevel=DEBUG
    fh.setFormatter(logging.Formatter('[ %(levelname)-8s] %(asctime)s | %(name)-32s %(funcName)-24s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logger = getLogger(__name__)
    logger.addHandler(fh)

    cde = ChatDataExtractor()
    cde.extract_from_keyword(input('keyword:'))