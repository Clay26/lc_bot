import datetime
import logging
from discord.ext import commands, tasks
from Utils import TableCache
from Entities import UserEntity

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=11, minute=00, tzinfo=utc)

def parse_embed_fields(dailyLCFields, fieldName):
    for field in dailyLCFields:
        if (field.name.lower() == fieldName.lower()):
            return field.value


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
        userEntity = self.load_user_cache(user.id)
        dailyLCQuestion = message.embeds[0]

        self.increment_queston_difficulty(userEntity, dailyLCQuestion)
        self.check_streak(userEntity, message)

    def increment_queston_difficulty(self, userEntity, dailyLCQuestion):
        difficulty = parse_embed_fields(dailyLCQuestion.fields, 'difficulty')
        if (difficulty.lower() == 'easy'):
            userEntity.numEasy += 1
        elif (difficulty.lower() == 'medium'):
            userEntity.numMedium += 1
        else:
            userEntity.numHard += 1

    def check_streak(self, userEntity, dailyLCMessage):
        now = datetime.datetime.now(utc)

        todayNewLCTime = datetime.datetime.combine(now.date(), time)
        yesterdayLCTime = todayNewLCTime - datetime.timedelta(days=1)
        tomorrowLCTime = todayNewLCTime + datetime.timedelta(days=1)

        dailyLCDate = dailyLCMessage.created_at

        if dailyLCDate >= todayNewLCTime and dailyLCDate < tomorrowLCTime:
            userEntity.completedToday = True
            if (userEntity.currStreakStartDate is None):
                userEntity.currStreakStartDate = now

    def save_user_cache(self, user):
        self.userCache.save_entity(user)

    def load_user_cache(self, userId):
        user = self.userCache.load_entity(userId)
        if (user is None):
            user = UserEntity(userId)

        return user
