import datetime
import logging
from discord.ext import commands, tasks
from Utils import TableCache
from Entities import UserEntity

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=11, minute=00, tzinfo=utc)


class StatsLC(commands.Cog):
    def __init__(self, bot, connectionString):
        self.bot = bot
        self.daily_stats_update.start()
        self.logger = logging.getLogger('discord.StatsLC')

        self.userCache = TableCache(UserEntity)
        self.userCache.initialize_table(connectionString)

    def cog_unload(self):
        self.daily_stats_update.cancel()

    @tasks.loop(time=time)
    async def daily_stats_update(self):
        self.logger.debug("Preparing to update users' stats.")
        self.logger.info("Successfully updated users' stats")

    def log_user_completion(self, message, user):
        print("YES")

    def save_user_cache(self, user):
        self.userCache.save_entity(user)

    def load_user_cache(self, userId):
        user = self.userCache.load_entity(userId)
        return user
