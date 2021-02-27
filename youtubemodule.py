#! /usr/bin/env python3
import asyncio
import datetime
import json
import os
import re
import sqlite3
import shutil
import time
import sys
import urllib

import youtube_dl

from db_connect import DatabaseConnect
from utils import (
    OverlappingError
)
import property


class YoutubeModule():
    def __init__(self):
        pass

    def data_check(self, url, ydl_ops={}):
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                sql = 'select id from download where id = ?'
                result = db.execute(sql, self.get_videoid(url))
                if result.fetchall() != []:
                    message = 'This Video is being downloaded.'
                    raise OverlappingError(message)
            except Exception as e:
                raise e

        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                sql = 'select id from archive where id = ?'
                result = db.execute(sql, self.get_videoid(url))
                if result.fetchall() != []:
                    message = 'Error: This video has already been downloaded.'
                    raise OverlappingError(message)
            except Exception as e:
                raise e

        try:
            info = self.get_info(url=url)
        except Exception as e:
            info = e

        if type(info) == dict:
            title = '%(title)s' % info
            message = 'Video title : ' + title + '\n' \
                'Download start...'
            return message

        if type(info) == youtube_dl.utils.DownloadError:
            error = str(info.exc_info[1])
            if 'This live event will begin in' in error:
                message = str(info.exc_info[1]) + '. Will be downloaded in ' + \
                    str(info.exc_info[1]).replace(
                        'This live event will begin in ', '')
                return message
            elif 'Premieres' in error:
                message = str(info.exc_info[1]) + '. Will be downloaded in ' + \
                    str(info.exc_info[1]).replace(
                        'Premieres ', '')
                return message
        else:
            raise info

    def download_video(self, url):
        is_download = False
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                now = datetime.datetime.now()
                date = now.strftime('%Y/%m/%d %H:%M:%S')
                sql = 'insert into download values(?,?,?,?)'
                result = db.execute(sql, self.get_videoid(url), url, date, None)
            except Exception as e:
                raise e

        while is_download != True:
            try:
                info = self.get_info(url)
                is_download = True
            except youtube_dl.utils.DownloadError as e:
                if str(e.exc_info[1]) == 'Video unavailable':
                    info = e
                    break
                info = e
            except youtube_dl.utils.ExtractorError as e:
                info = e
            except Exception as e:
                raise e

            sleeptime = self.live_timer(info=info)
            time.sleep(sleeptime)

        if is_download == True:
            now = datetime.datetime.now()

            start_time = now.strftime('%Y/%m/%d %H:%M')
            with DatabaseConnect(property.DOWNLOAD_DATA) as db:
                try:
                    sql = 'update download set starttime = ?'
                    result = db.execute(sql, start_time)
                except Exception as e:
                    raise e

            date = now.strftime('%Y%m%d%H%M')
            ng_word = {
                '\\': '＼',
                '/': '／',
                ':': '：',
                '<': '＜',
                '>': '＞',
                '|': '｜',
                '?': '？',
            }
            title = date + '_%(id)s_%(title)s' % info
            title = title.translate(str.maketrans(ng_word))
            outpath = os.getcwd() + '/tmp/' + title + '.%(ext)s'

            start_time = now.strftime('%Y/%m/%d %H:%M')

            with youtube_dl.YoutubeDL(self.ops(info=info, outpath=outpath)) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                except youtube_dl.utils.DownloadError as e:
                    info = e

            time.sleep(10)

            shutil.move(outpath % info, '/mnt/media/Youtube/' + title + '.%(ext)s' % info)

        now = datetime.datetime.now()
        id = self.get_videoid(url)
        uploader    = '%(uploader)s' % info
        channel_id  = '%(channel_id)s' % info
        channel_url = '%(channel_url)s' % info
        upload_date = '%(upload_date)s' % info
        end_time    = now.strftime('%Y/%m/%d %H:%M')
        title       = '%(title)s' % info
        description = '%(description)s' % info
        webpage_url = '%(webpage_url)s' % info
        is_live     = '%(is_live)s' % info
        width       = '%(width)s' % info
        height      = '%(height)s' % info

        
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                sql = 'insert into archive values(?,?,?,?,?,?,?,?,?,?,?,?,?)'
                result = db.execute(sql, id, uploader, channel_id, channel_url, upload_date, start_time, end_time, title, description, webpage_url, is_live, width, height)
            except Exception as e:
                raise e

        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                sql = 'delete from download where id = ?'
                result = db.execute(sql, id)
            except Exception as e:
                raise e

        return info

    def get_info(self, url):
        with youtube_dl.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
        return info

    def live_timer(self, info):
        if type(info) == dict:
            return 0
        elif type(info) == youtube_dl.utils.DownloadError:
            if 'This live event will begin in' in str(info.args) or 'Premiere' in str(info.args):

                # 'ERROR: This live event will begin in 77 minutes.'
                # 'ERROR: Premieres in 7 hours'
                args = str(info.args).split()
                time = -1
                for arg in args:
                    try:
                        time = int(arg) - 0.5
                    except:
                        if 'days' in arg:
                            time = time * 86400
                        elif 'hours' in arg:
                            time = time * 3600
                        elif 'minutes' in arg:
                            time = time * 60
                        elif 'few' in arg:
                            time = 5
                        elif 'shortly' in arg:
                            time = 5
                        else:
                            pass
                if time >= 0:
                    return time
                else:
                    raise info
            else:
                raise info
        else:
            raise info

    def ops(self, info, outpath):
        ydl_ops = {
            "outtmpl": outpath,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mkv',
            'noplaylist': True,
            'keepvideo': False,
            'nooverwrites': True,
            'hls_use_mpegts': True,
            'socket_timeout': 300,
            # 'postprocessors': [{
            # 'key': 'FFmpegFixupM4a',
            # }],
        }
        return ydl_ops

    def get_videoid(self, url):
        parsed_url = urllib.parse.urlparse(url)
        video_id = urllib.parse.parse_qs(parsed_url.query)['v']
        return ''.join(video_id)


if __name__ == "__main__":
    ydm = YoutubeModule()
    url = input('URL: ')
    try:
        info = ydm.download_video(url)
    except Exception as e:
        info = e
    print(info)
    # print(type(title))
    message = ydm.live_timer(info)
    print(message)
