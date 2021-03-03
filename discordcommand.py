#! /usr/bin/env python3
#---standard library---
import sqlite3
import traceback

#---third party library---
from discord.ext import commands

#---local library---
from db_connect import DatabaseConnect
import property


class MyBot(commands.Bot):

    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)

        # Cogをpropartyのリストからロード
        for cog in property.INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
                print('Success: Cog loaded (' + cog + ')')
            except Exception as e:
                raise e
                # traceback.print_exc()

    async def on_ready(self):
        print('----------------')
        print(self.user.name    )
        print(self.user.id      )
        print('----------------')

        with DatabaseConnect(property.DOWNLOAD_DATA) as db:
            try:
                db.execute('create table if not exists download' + property.DOWNLOAD_DATALIST)
                db.execute('create table if not exists archive' + property.ARCHIVE_DATALIST)
            except Exception as e:
                raise e

if __name__ == '__main__':
    bot = MyBot(command_prefix='!')
    bot.run(property.DISCORD_KEY)