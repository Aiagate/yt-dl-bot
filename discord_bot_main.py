#! /usr/bin/env python3
# ---standard library---
import sqlite3
import traceback
import logging
from logging import DEBUG, INFO, Logger, getLogger

# ---third party library---
from discord.ext import commands

# ---local library---
from db_connect import DatabaseConnect
import property


class MyBot(commands.Bot):

    def __init__(self, command_prefix):
        # loggerを作成
        self.logger = getLogger(__name__)

        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)

        # Cogをpropartyのリストからロード
        for cog in property.INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
                self.logger.info('Success: Cog loaded ({})'.format(cog))
            except Exception as e:
                raise e
                # traceback.print_exc()

    async def on_ready(self):
        self.logger.info('----------------')
        self.logger.info(self.user.name)
        self.logger.info(self.user.id)
        self.logger.info('----------------')
        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                db.execute('create table if not exists download' +
                           property.DOWNLOAD_DATALIST)
                db.execute('create table if not exists archive' +
                           property.ARCHIVE_DATALIST)
            except Exception as e:
                raise e


if __name__ == '__main__':
    logging.basicConfig(
        level=INFO,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-24s %(funcName)-16s| %(message)s',
        # format='[ %(levelname)-8s] %(asctime)s | %(name)s\t%(funcName)s\t| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = getLogger(__name__)

    bot = MyBot(command_prefix='!')
    bot.run(property.DISCORD_KEY)