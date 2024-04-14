import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import logging.handlers
from LCBot import DailyLC, StatsLC

class LCBot():
    def __init__(self):
        self.description = '''Sends a daily leet code challenge.'''
        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.message_content = True

        load_dotenv()
        self.environment = os.getenv('ENVIRONMENT', 'development')

        self.bot = commands.Bot(command_prefix='?', description=self.description, intents=self.intents)

        self.setup_logging()
        self.register_events()
        self.register_commands()

        self.logger.setLevel(logging.DEBUG)

    def setup_logging(self):
        if self.environment == 'production':
            logFilePath = '/home/LogFiles/discord.log'
            loggingLevel = logging.ERROR
            lcLoggingLevel = logging.INFO
        else:
            logFilePath = './discord.log'
            loggingLevel = logging.INFO
            lcLoggingLevel = logging.DEBUG

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

        self.logger.setLevel(lcLoggingLevel)
        logging.getLogger('discord.DailyLC').setLevel(lcLoggingLevel)
        logging.getLogger('discord.StatsLC').setLevel(lcLoggingLevel)
        logging.getLogger('discord.TableCache').setLevel(lcLoggingLevel)

    def register_events(self):
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
            print('------')
            CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')
            await self.bot.add_cog(DailyLC(self.bot, CONNECTION_STRING))
            print('Added DailyLC bot')
            await self.bot.add_cog(StatsLC(self.bot, CONNECTION_STRING))
            print('Added StatsLC bot')

        @self.bot.event
        async def on_reaction_add(reaction, user):
            if (reaction.message.author == self.bot.user
                and reaction.emoji == '✅'):
                statsLC = self.bot.get_cog('StatsLC')
                statsLC.test()

    def register_commands(self):
        @self.bot.command()
        async def localTest(ctx):
            if self.environment == 'development':
                dailyLC = self.bot.get_cog('DailyLC')

                # Testing cache loading
                channelId = dailyLC.load_channel_cache(ctx.guild.id)
                await ctx.send(f'Got channelId [{channelId}] from cache.')

                if (channelId > 0):
                    # Test cache saving
                    dailyLC.save_channel_cache(ctx.guild.id, channelId)
                    await ctx.send(f'Saved server [{ctx.guild.id}] with channelId [{channelId}] to cache.')
                else:
                    await ctx.send(f'Skipping server [{ctx.guild.id}] channelId cache saving since no channel is currently set.')

                # Testing message retrieval
                message = await dailyLC.get_daily_question_message()

                await ctx.send(embed=message)

        @self.bot.command()
        async def test(ctx):
            dailyLC = self.bot.get_cog('DailyLC')
            message = await dailyLC.get_daily_question_message()
            await ctx.send(embed=message)

        @self.bot.command()
        async def fullTest(ctx):
            dailyLC = self.bot.get_cog('DailyLC')
            await dailyLC.send_daily_question()

        @self.bot.command()
        async def setChannel(ctx, channelId: int):
            dailyLC = self.bot.get_cog('DailyLC')
            await dailyLC.set_channel_id(ctx, channelId)

    def run(self):
        DISCORD_API_KEY = os.getenv('DISCORD_BOT_API_KEY')

        if not DISCORD_API_KEY:
            self.logger.error("Unable to fetch API key.")
        else:
            self.logger.debug("Logging in as grinder bot.")
            self.bot.run(DISCORD_API_KEY, log_handler=None)
            self.logger.info("Successfully logged in as the grinder bot.")
