#! /usr/bin/env python3

from pytchat import LiveChat
import time
import datetime
import os
import importlib
import ffmpeg
import numpy
import sqlite3
import shutil
import logging
from logging import getLogger
import matplotlib.pyplot as plt
from multiprocessing import Pool
from moviepy.editor import *
from collections import deque

import db_connect
import youtubeapi
# from db_connect import DatabaseConnect
from utils import (
    OverlappingError
)
import property


class ChatDataModule():
    def __init__(self, video_id, url=None, livedetail=None):
        self.logger = getLogger(__name__)
        importlib.reload(importlib)
        importlib.reload(db_connect)
        self.url = url
        self.video_id = video_id
        self.date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
        # self.db_name = '/mnt/media/Youtube/databases/chatdata_I4I_HJenWkQ.db'
        self.db_name = os.getcwd() + '/databases/chatdata_' + \
            self.date + '_' + video_id + '.db'
        self.image_name = 'scoregraph_' + self.date + '_' + video_id + '.png'
        self.image_path = os.getcwd() + '/tmp/' + self.image_name
        self.starttime = 0
        self.endtime = 0

        self.livedetail = livedetail
        # self.livedetail = ytapi.get_livedetail(self.video_id)

    def count_score(self):
        ytapi = youtubeapi.YoutubeApi()

        self.livedetail = ytapi.get_livedetail(self.video_id)

        self.starttime = ytapi.get_starttime_UNIX(self.livedetail)
        self.endtime = ytapi.get_endtime_UNIX(self.livedetail)
        self.logger.info('Video start time [{}]'.format(self.starttime))
        self.logger.info('Video end time [{}]'.format(self.endtime))

        seektime = self.starttime
        score_data = []
        average_count = deque([1000] * 8)

        while seektime + 60000 <= self.endtime:
            score = 0
            with db_connect.DatabaseConnect(db_name=self.db_name) as db:
                try:
                    result = db.execute(
                        'select type,message from chatdata where timestamp > ? and timestamp < ?', seektime, seektime + 60000)
                    result_data = result.fetchall()
                except Exception as e:
                    raise e
            # score = 0
            score = len(result_data)
            '''
            for c in result_data:
                if c[0] == 'superSticker' or c[0] == 'superChat' or c[0] == 'newSponsor':
                    score = score + 20

                score_word = [
                    # ':',
                    '!', '！',
                    '?', '？',
                    'w', 'W', 'ｗ', 'Ｗ',
                    '草'
                ]
                if c[1] in score_word:
                    score = score + 10

                score = score + 1
            '''

            '''
            t = str(self.starttime) + '\t' +\
                str(seektime) + '\t' +\
                str(self.endtime) + '\t' +\
                str(score) + '\t' +\
                str((sum(average_count)+1) / len(average_count)) + '\t' +\
                str(score / ((sum(average_count)+1) / len(average_count)))
            print(t)
            '''

            comment_count = len(result_data)

            if comment_count > 0:
                score = score / (sum(average_count) / len(average_count))

                average_count.append(comment_count)
                average_count.popleft()

            self.logger.info('score {}'.format(score))
            score_data.append(score)
            seektime = seektime + 30000

        self.logger.debug('score data:'.format(score_data))
        return score_data

    def plot_peak(self, score_data):
        max_score = max(score_data)
        score_size = len(score_data)

        plt.figure()
        plt.plot([i * 30 for i in list(range(score_size))], score_data)
        plt.grid(axis='y', linestyle='dotted')
        plt.savefig(self.image_path)

    def get_peaktime(self, score_data):
        max_score = max(score_data)
        score_size = len(score_data)

        peaktime = []
        i = 0
        limit = 0.4
        while i < score_size:
            if score_data[i] > max_score * limit:
                peaktime_sec = max(i - 1, 0)
                l = 2
                while l >= 0 and i < score_size:
                    if score_data[i] > max_score * limit:
                        l = 2
                    else:
                        l = l - 1
                    i = i + 1
                peaktime_sec = peaktime_sec * 30
                peaktime.append(peaktime_sec)
            i = i + 1
        return peaktime

    def get_chatdata(self):
        chat = LiveChat(video_id=self.video_id)

        with db_connect.DatabaseConnect(db_name=self.db_name) as db:
            try:
                db.execute('drop table if exists chatdata')
                db.execute('create table if not exists chatdata ' +
                           property.CHAT_DATALIST)
            except Exception as e:
                raise e

        while chat.is_alive():
            try:
                data = chat.get()
                items = data.items
                for c in items:
                    self.logger.info(
                        f"{c.datetime} {c.timestamp} [{c.author.name}]- {c.message}")
                    # print(type(c.author.name))
                    with db_connect.DatabaseConnect(db_name=self.db_name) as db:
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

            except:
                pass
            '''
            except KeyboardInterrupt:
                # chat.terminate()
                break
            except Exception as e:
                # chat.terminate()
                raise e
            '''
            time.sleep(3)
        return 'Success!'

    def cut_movie(self, file_path, title, date, pool):
        self.logger.debug('video id: {}'.format(self.video_id))
        pool.wait()
        cut_time = self.get_peaktime(self.count_score())
        self.logger.debug('video id: {}'.format(cut_time))

        for time in cut_time:
            start_time = time[0]
            end_time = time[1]
            filename = date + '_' + self.video_id + '_' + title + \
                '_' + str(start_time) + '-' + str(end_time) + '.mkv'
            save_path = os.getcwd() + '/tmp/' + filename

            video_info = ffmpeg.probe(file_path)
            duration = float(video_info['format']['duration'])

            start_time = min(start_time, duration)
            stride = min(end_time, duration) - start_time

            stream = ffmpeg.input(file_path, ss=start_time, t=stride)
            stream = ffmpeg.output(stream, save_path, c="copy")
            stream = ffmpeg.overwrite_output(stream)
            try:
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
                shutil.move(save_path, '/mnt/media/Youtube/' +
                            date[:10] + '/' + filename)
            except ffmpeg.Error as e:
                self.logger.error('stdout: {}'.format(e.stdout.decode('utf8')))
                self.logger.error('stderr: {}'.format(e.stderr.decode('utf8')))
                database_name = 'chatdata_' + self.date + '_' + self.video_id + '.db'
                database_path = 'databases/'
                out_path = "/mnt/media/Youtube/databases/"
                if not os.path.exists(out_path):
                    os.mkdir(out_path)
                shutil.move(database_path + database_name,
                            out_path + database_name)
                os.remove(file_path)
                raise e

        database_name = 'chatdata_' + self.date + '_' + self.video_id + '.db'
        database_path = 'databases/'
        out_path = "/mnt/media/Youtube/databases/"
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        shutil.move(database_path + database_name, out_path + database_name)
        os.remove(file_path)

    def get_highlight(self):
        pool = Pool(1)
        result = pool.apply_async(self.get_chatdata)
        self.logger.info('get chat')
        result.wait()
        self.logger.info('sleep')

        ytapi = youtubeapi.YoutubeApi()
        while ytapi.get_islive(ytapi.get_livedetail(self.video_id)) == True:
            time.sleep(60)

        self.livedetail = ytapi.get_livedetail(self.video_id)

        self.logger.info('get score')
        score_data = self.count_score()
        self.plot_peak(score_data)
        self.logger.info('get peaktime')
        peak_time = self.get_peaktime(score_data)
        highlight_urls = []
        for sec in peak_time:
            url = self.url + '&t=' + str(sec) + 's'
            self.logger.info('url: {}'.format(url))
            highlight_urls.append([sec, url])
        out_path = "/mnt/media/Youtube/databases/"
        shutil.move(self.db_name, out_path)  # + self.db_name)
        self.logger.info('move database')
        return highlight_urls


if __name__ == '__main__':
    import logging
    from logging import DEBUG, INFO, Logger, getLogger
    logging.basicConfig(
        level=INFO,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-24s %(funcName)-16s| %(message)s',
        # format='[ %(levelname)-8s] %(asctime)s | %(name)s\t%(funcName)s\t| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    id = input('ID:')
    # cdm = ChatDataModule(id)  # 'CGTaqNWE7HU'
    # print(chatviewer.video_id)
    # chatviewer.test()
    # chatviewer.cut_movie(None,None,None,None)
    # cdm.get_chatdata()
    # data = chatviewer.count_score()
    # chatviewer.plot_peak(data)
    # chatviewer.cut_movie('/home/dorothy/work/python/discord_Youtube-dlBot/tmp/202103072134_on1Tv63h8y8_【#にじARK​​】異世界農家　舞元【にじさんじ／舞元啓介】.mp4')
    # cut_time = chatviewer.get_peaktime(data)
    # print(cut_time)
    # chatviewer.plot_peak(data)

    cdm = ChatDataModule('MPX-err6GTo')  # 'CGTaqNWE7HU'
    cdm.db_name = 'databases/chatdata_TEST_MPX-err6GTo.db'
    cdm.get_highlight()
    # score = cdm.count_score()
    # cdm.plot_peak(score)

