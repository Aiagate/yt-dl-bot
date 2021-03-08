#! /usr/bin/env python3

from pytchat import LiveChat
import time
import os
import ffmpeg
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

        # print(score_data)
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
        i = 0
        while i < score_size:
            if score_data[i] > max_score * 0.6:
                start_time = max(i - 4, 0)
                l = 4
                while l >= 0 and i < score_size:
                    if score_data[i] > max_score * 0.6:
                        l = 4
                    else:
                        l = l - 1
                    i = i + 1

                end_time = i

                start_time = start_time * 30
                end_time = end_time * 30
                cut_time.append([start_time, end_time])

            i = i + 1

        return cut_time



    def get_chatdata(self):
        
        chat = LiveChat(video_id=self.video_id)

        with DatabaseConnect(db_name=self.db_name) as db:
            try:
                db.execute('drop table if exists ' + property.CHAT_DATALIST)
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

    def cut_movie(self, file_path, title, date):
        cut_time = self.get_peaktime(self.count_score())
        print(cut_time)


        for time in cut_time:
            start_time = time[0]
            end_time = time[1]
            print('+++++++++++++++++++++++++')
            print(start_time)
            print(end_time)
            print('+++++++++++++++++++++++++')

            filename = date + '_' +self.video_id + '_' + title + '_' + str(start_time) + '-' + str(end_time) + '.mkv'
            save_path = os.getcwd() + '/tmp/' + filename

            video_info = ffmpeg.probe(file_path)
            duration = float(video_info['format']['duration'])

            start_time = min(start_time,duration)
            stride = min(end_time,duration) - start_time

            stream = ffmpeg.input(file_path, ss=start_time, t=stride)
            stream = ffmpeg.output(stream, save_path, c="copy")
            stream = ffmpeg.overwrite_output(stream)
            try:
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
                database_name = 'chatdata_' + video_id + '.db'
                database_path = 'databases/'
                out_path = "/mnt/media/Youtube/databases/"
                if not os.path.exists(out_path):
                    os.mkdir(out_path)
                shutil.move(database_path + database_name, out_path + database_name)
                os.remove(file_path)
                raise e
            
            shutil.move('chatdata_' + self.video_id + '.db', '/mnt/media/Youtube/chatdata/' + filename)

        database_name = 'chatdata_' + video_id + '.db''
        database_path = 'databases/'
        out_path = "/mnt/media/Youtube/databases/"
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        shutil.move(database_path + database_name, out_path + database_name)
        os.remove(file_path)


if __name__ == '__main__':
    id = input('ID:')
    chatviewer = ChatViewModule(id) #'CGTaqNWE7HU'
    # chatviewer.get_chatdata()
    data = chatviewer.count_score()
    chatviewer.plot_peak(data)
    chatviewer.cut_movie('/home/dorothy/work/python/discord_Youtube-dlBot/tmp/202103072134_on1Tv63h8y8_【#にじARK​​】異世界農家　舞元【にじさんじ／舞元啓介】.mp4')
    cut_time = chatviewer.get_peaktime(data)
    print(cut_time)
    # chatviewer.plot_peak(data)


