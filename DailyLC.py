import pytz
import datetime
from discord.ext import commands, tasks

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=3, minute=36, tzinfo=utc)

class DailyLC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_task.start()
        print("Starting DailyLC")
        print(datetime.now(utc))

    def cog_unload(self):
        self.my_task.cancel()

    @tasks.loop(time=time)
    async def my_task(self):
        print("My task is running!")
