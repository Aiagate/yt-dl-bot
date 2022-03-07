#! ./.venv/bin/python

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
                self.logger.info(f'Success: Cog loaded ({cog})')
            except Exception as e:
                self.logger.error(e)
                raise e
                # traceback.print_exc()

    async def on_ready(self):
        self.logger.info('----------------')
        self.logger.info(self.user.name)
        self.logger.info(self.user.id)
        self.logger.info('----------------')

if __name__ == '__main__':
    logging.basicConfig(
        level=INFO,
        format='[ %(levelname)-8s] %(asctime)s | %(name)-16s %(funcName)-16s| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh = logging.FileHandler(filename='log/discord_bot_main.log', encoding='utf-8')
    fh.setLevel=INFO
    fh.setFormatter(logging.Formatter('[ %(levelname)-8s] %(asctime)s | %(name)-16s %(funcName)-24s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    dlogger = getLogger('discord')
    dlogger.addHandler(fh)
    logger = getLogger(__name__)
    logger.addHandler(fh)

    bot = MyBot(command_prefix='!')
    bot.run(property.DISCORD_KEY)
    logger2 = getLogger('youtubemodule')
    logger2.addHandler(fh)

