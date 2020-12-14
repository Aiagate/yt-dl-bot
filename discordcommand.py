#! /usr/bin/env python3
from discord.ext import commands
import traceback
import property


class MyBot(commands.Bot):

    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)

        for cog in property.INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')


if __name__ == '__main__':
    # command_prefixはコマンドの最初の文字として使うもの。 e.g. !ping
    bot = MyBot(command_prefix='!')
    bot.run(property.KEY)