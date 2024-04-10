import discord
from discord.ext import commands, tasks
import random
import datetime
import asyncio
import time
import logging
import logging.handlers
from apikeys import BOTTOKEN
from DailyLC import DailyLC


description = '''Sends a daily leet code challenge.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

async def send_daily_message():
    channel = bot.get_channel(412802660719263744)
    if channel:
        await channel.send("Your daily message.")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await send_daily_message()
    await bot.add_cog(DailyLC(bot))


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


bot.run(BOTTOKEN, log_handler=None)
