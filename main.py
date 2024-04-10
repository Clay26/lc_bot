import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import random
import datetime
import asyncio
import time
import logging
import logging.handlers
from DailyLC import DailyLC
from LeetQuery import LeetQuery


description = '''Sends a daily leet code challenge.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(DailyLC(bot))
    print('Added DailyLC bot')


@bot.command()
async def test(ctx):
    dailyLC = bot.get_cog('DailyLC')
    message = await dailyLC.send_daily_question()


@bot.command()
async def setChannel(ctx, channelId: int):
    dailyLC = bot.get_cog('DailyLC')
    await dailyLC.set_channel_id(ctx, channelId)


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_BOT_API_KEY')

if not DISCORD_API_KEY:
    logger.error("Unable to fetch API key.")
else:
    logger.info("Logging in as grinder bot.")
    bot.run(DISCORD_API_KEY, log_handler=None)
    logger.debug("Sucessfully logged in as the grinder bot.")
