import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import logging.handlers
from DailyLC import DailyLC

class LCBot():
    def __init__(self):
        self.description = '''Sends a daily leet code challenge.'''
        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.message_content = True

        self.bot = commands.Bot(command_prefix='?', description=self.description, intents=self.intents)

        self.setup_logging()
        self.register_events()
        self.register_commands()

    def setup_logging(self):
        load_dotenv()

        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'production':
            log_file_path = '/home/LogFiles/discord.log'
        else:
            log_file_path = './discord.log'

        logging.basicConfig(filename=log_file_path, level=logging.INFO)
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        logging.getLogger('discord.http').setLevel(logging.INFO)

        handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def register_events(self):
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
            print('------')
            await self.bot.add_cog(DailyLC(self.bot))
            print('Added DailyLC bot')

    def register_commands(self):
        @self.bot.command()
        async def test(ctx):
            dailyLC = self.bot.get_cog('DailyLC')
            message = await dailyLC.send_daily_question()

        @self.bot.command()
        async def setChannel(ctx, channelId: int):
            dailyLC = self.bot.get_cog('DailyLC')
            await dailyLC.set_channel_id(ctx, channelId)

    def run(self):
        DISCORD_API_KEY = os.getenv('DISCORD_BOT_API_KEY')

        if not DISCORD_API_KEY:
            logging.error("Unable to fetch API key.")
        else:
            logging.info("Logging in as grinder bot.")
            self.bot.run(DISCORD_API_KEY, log_handler=None)
            logging.debug("Successfully logged in as the grinder bot.")
