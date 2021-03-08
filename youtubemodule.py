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
from multiprocessing import Pool

import youtube_dl

from db_connect import DatabaseConnect
from chatviewmodule import ChatViewModule
from utils import (
    OverlappingError
)
import property


class YoutubeModule():
    def __init__(self):
        pass

    def data_check(self, url, ydl_ops={}):

        #ダウンロード進行中の動画と同じ動画のダウンロードを制限
        '''
        ライブ配信かアーカイブかによって制限の解除を行うように改良予定
        '''
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                sql = 'select id from download where id = ?'
                result = db.execute(sql, self.get_videoid(url))
                if result.fetchall() != []:
                    message = 'This Video is being downloaded.'
                    raise OverlappingError(message)
            except Exception as e:
                raise e
        
        #重複した動画のダウンロードを制限
        '''
        ライブ配信とそのアーカイブの場合は制限しないように改良予定
        '''
        '''
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                sql = 'select id from archive where id = ?'
                result = db.execute(sql, self.get_videoid(url))
                if result.fetchall() != []:
                    message = 'Error: This video has already been downloaded.'
                    raise OverlappingError(message)
            except Exception as e:
                raise e
        '''

        #URLから動画情報を抽出
        try:
            info = self.get_info(url=url)

            #動画情報の抽出が正常終了した場合、メッセージを返す
            title = '%(title)s' % info
            message = 'Video title : ' + title + '\n' \
                      'Download start...'
            return message
        except youtube_dl.utils.DownloadError as e:
            error = str(e.exc_info[1])
            if 'This live event will begin in' in error:
                message = str(e.exc_info[1]) + '. Will be downloaded in ' + \
                          str(e.exc_info[1]).replace('This live event will begin in ', '')
                return message
            elif 'Premieres' in error:
                message = str(e.exc_info[1]) + '. Will be downloaded in ' + \
                          str(e.exc_info[1]).replace('Premieres ', '')
                return message
            else:
                raise e
        except Exception as e:
            raise e

    def download_video(self, url):
        is_download = False

        #ダウンロード進行中のデータテーブルに動画情報を登録
        '''
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                now = datetime.datetime.now()
                date = now.strftime('%Y/%m/%d %H:%M:%S')
                sql = 'insert into download values(?,?,?,?)'
                result = db.execute(sql, self.get_videoid(url), url, date, None) #主キーにIDを使用するのをやめる
            except Exception as e:
                raise e
        '''

        #ライブ配信の場合、ライブ開始まで待機
        while is_download != True:
            try:
                #ダウンロード処理
                info = self.get_info(url)
                is_download = True
                break
            except youtube_dl.utils.DownloadError as e: #動画URLが有効でない場合にエラーを返す
                info = e
            except youtube_dl.utils.ExtractorError as e: #動画の抽出に失敗した場合は待機するため処理を続行する
                info = e
            except Exception as e:
                raise e

            #待機時間を計算しジョブを待機させる
            sleeptime = self.live_timer(info=info)
            time.sleep(sleeptime)

        # is_download==True の場合、ダウンロード処理を開始する
        if is_download == True:
            now = datetime.datetime.now()

            #ダウンロード開始時刻をダウンロード進行中ののデータテーブルに追記
            '''
            start_time = now.strftime('%Y/%m/%d %H:%M')
            with DatabaseConnect(property.DOWNLOAD_DATA) as db:
                try:
                    sql = 'update download set starttime = ?'
                    result = db.execute(sql, start_time)
                except Exception as e:
                    raise e
            '''


            #ファイルパス・ファイル名を作成
            date = now.strftime('%Y-%m-%d_%H%M')
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
            video_title = '%(title)s' % info
            title = title.translate(str.maketrans(ng_word))
            video_title = video_title.translate(str.maketrans(ng_word))
            outpath = '/mnt/cache/' + title + '.%(ext)s'
            # outpath = os.getcwd() + '/tmp/' + title + '.%(ext)s'

            start_time = now.strftime('%Y/%m/%d %H:%M')

            #ダウンロード処理
            cvm = ChatViewModule(self.get_videoid(url))
            pool = Pool(1)
            result = pool.apply_async(cvm.get_chatdata)

            with youtube_dl.YoutubeDL(self.ops(info=info, outpath=outpath)) as ydl:
                info = ydl.extract_info(url, download=True)

            # print(result.get())

            #ダウンロードプロセスによるファイルのロックが解除されるまで待つ
            # time.sleep(10)
            
            #ファイルをtmpフォルダから移動
            save_path = "/mnt/media/Youtube/" + now.strftime('%Y-%m-%d') + '/'
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            shutil.copy2(outpath % info,  save_path + title + '.%(ext)s' % info)
            return [info, outpath % info, video_title, date, result]

        '''
        データベースへの登録は別関数に実装すべき？
        '''
        '''
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
        '''


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
        info = ydm.get_info(url)
        print('%(is_live)s' % info)
    except Exception as e:
        print('==================================================================')
        print(type(e))
        print('==================================================================')
        print(e.args)
        print('==================================================================')
        print(e.exc_info)
        print('==================================================================')
        print(type(e.exc_info[0]))
        print(e.exc_info[0])
        print('==================================================================')
        print(type(e.exc_info[1]))
        print(e.exc_info[1])
        print('==================================================================')
        print(type(e.exc_info[2]))
        print(e.exc_info[2])
        print('==================================================================')
    # print(type(title))
    # message = ydm.live_timer(info)
    # print(message)
