#! /usr/bin/env python3

from pytchat import LiveChat
import time
import os
import numpy
import sqlite3
import shutil
import matplotlib.pyplot as plt
from moviepy.editor import *

from db_connect import DatabaseConnect
from utils import (
    OverlappingError
)
import property

class ChatViewModule():
    def __init__(self, video_id):
        self.video_id = video_id
        self.db_name = 'databases/chatdata_' + video_id + '.db'
        self.starttime = 0


    def count_score(self):
        with DatabaseConnect(db_name=self.db_name) as db:
            try:
                result = db.execute('select min(timestamp) from chatdata')
                self.starttime = result.fetchone()[0]
                result = db.execute('select max(timestamp) from chatdata')
                endtime = result.fetchone()[0]
            except Exception as e:
                raise e

        seektime = self.starttime
        score_data = []

        while seektime <= endtime:
            score = 0
            with DatabaseConnect(db_name=self.db_name) as db:
                try:
                    result = db.execute('select type,message from chatdata where timestamp > ? and timestamp < ?', seektime, seektime + 60000)
                    result_data = result.fetchall()
                except Exception as e:
                    raise e

            for c in result_data:
                if c[0] == 'superSticker' or c[0] == 'superChat':
                    score = score + 20
                
                score_word = [
                    '!', '！',
                    '?', '？',
                    'w', 'W','ｗ', 'Ｗ',
                    '草', 
                    ':'
                ]
                if c[1] in score_word:
                    score = score + 10
                
                score = score + 5

            score_data.append(score)

            seektime = seektime + 30000

        print(score_data)
        return score_data

    def plot_peak(self, score_data):
        max_score = max(score_data)
        score_size = len(score_data)

        plt.plot(range(score_size), score_data)
        plt.grid(axis='y', linestyle='dotted')
        plt.savefig(self.video_id + '.png')
    
    def get_peaktime(self, score_data):
        max_score = max(score_data)
        score_size = len(score_data)

        cut_time = []

        for i, score in enumerate(score_data):
            if score >= int(max_score * 0.8):
                index = 0
                seek = 0
                while index > 3:
                    if score_data >= int(max_score * 0.8):
                        index = 0
                        seek = seek + 1
                        continue
                    else:
                        index = index + 1

                start_time = max(0,i-4) * 30
                end_time = (i + 4 + seek) * 30
                cut_time.append([start_time ,end_time])

        return cut_time



    def get_chatdata(self):
        
        chat = LiveChat(video_id=self.video_id)

        with DatabaseConnect(db_name=self.db_name) as db:
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
                    with DatabaseConnect(db_name=self.db_name) as db:
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
        return 'Success!'

    def cut_movie(self, file_path):
        cut_time = self.get_peaktime(self.count_score())
        print(cut_time)

        for time in cut_time:
            start_time = time[0]
            end_time = time[1]
            print('+++++++++++++++++++++++++')
            print(start_time)
            print(end_time)
            print('+++++++++++++++++++++++++')

            filename = self.video_id + '_' + str(start_time) + '-' + str(end_time) + '.mp4'
            save_path = os.getcwd() + '/tmp/' + filename

            video = VideoFileClip(file_path)

            print(video.duration)

            start_time = min(start_time,video.duration - 1)
            end_time = min(end_time,video.duration - 1)

            print(start_time)
            print(end_time)
            print('==========================')

            if (end_time - start_time) < 5:
                continue

            video.subclip(start_time, end_time)
            video.write_videofile(save_path,fps=60)
            shutil.move(save_path, '/mnt/media/Youtube/' + filename)


if __name__ == '__main__':
    id = input('ID:')
    chatviewer = ChatViewModule(id) #'CGTaqNWE7HU'
    # chatviewer.get_chatdata()
    data = chatviewer.count_score()
    # chatviewer.plot_peak(data)
    cut_time = chatviewer.get_peaktime(data)
    print(cut_time)
    # chatviewer.plot_peak(data)


