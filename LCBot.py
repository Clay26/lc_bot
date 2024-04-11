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

        self.logger.setLevel(logging.DEBUG)

    def setup_logging(self):
        load_dotenv()

        environment = os.getenv('ENVIRONMENT', 'development')
        if environment == 'production':
            logFilePath = '/home/LogFiles/discord.log'
            loggingLevel = logging.ERROR
        else:
            logFilePath = './discord.log'
            loggingLevel = logging.INFO

        logging.basicConfig(filename=logFilePath, level=loggingLevel)
        logger = logging.getLogger('discord')
        logger.setLevel(loggingLevel)
        logging.getLogger('discord.http').setLevel(loggingLevel)

        handler = logging.handlers.RotatingFileHandler(
            filename=logFilePath,
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.logger = logging.getLogger('discord.LCBot')

        self.logger.setLevel(logging.DEBUG)
        logging.getLogger('discord.DailyLC').setLevel(logging.DEBUG)

    def register_events(self):
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
            print('------')
            CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')
            await self.bot.add_cog(DailyLC(self.bot, CONNECTION_STRING))
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
            self.logger.error("Unable to fetch API key.")
        else:
            self.logger.info("Logging in as grinder bot.")
            self.bot.run(DISCORD_API_KEY, log_handler=None)
            self.logger.debug("Successfully logged in as the grinder bot.")
