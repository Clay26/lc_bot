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
        for user in self.bot.get_members():
            userEntity = self.load_user_cache(user.id)

            currStreak = userEntity.get_current_streak()

            if userEntity.completedToday:
                # Check if today's completion results in a new longest streak
                if currStreak > userEntity.longestStreak:
                    self.logger.info(f'User [{userEntity.id}] has a new longest streak!')
                    userEntity.longestStreak = currStreak
            else:
                # Reset current streak if they haven't completed today
                userEntity.currStreakStartDate = None

            # Reset the daily completion flag for all users
            userEntity.completedToday = False

            # Save changes to the cache
            self.save_user_cache(userEntity)

        self.logger.info("Successfully updated users' stats")

    def log_user_completion(self, message, user):
        self.logger.debug(f'Logging stats for user [{user.id}].')
        userEntity = self.load_user_cache(user.id)
        dailyLCQuestion = message.embeds[0]

        self.increment_queston_difficulty(userEntity, dailyLCQuestion)
        self.check_streak(userEntity, message)
        self.save_user_cache(userEntity)

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

        nextRelease = datetime.datetime.combine(now.date(), time)

        if now > nextRelease:
            # Before 11 AM UTC, use yesterday as latest release
            nextRelease = nextRelease + datetime.timedelta(days=1)

        latestRelease = nextRelease - datetime.timedelta(days=1)

        completedDailyLCDate = dailyLCMessage.created_at

        if latestRelease <= completedDailyLCDate and completedDailyLCDate < nextRelease:
            self.logger.info(f'User [{userEntity.id}] completed the Daily LC!')
            userEntity.completedToday = True
            if (userEntity.currStreakStartDate is None):
                self.logger.info(f'Starting streak for user [{userEntity.id}].')
                userEntity.currStreakStartDate = latestRelease.date()

    def save_user_cache(self, user):
        self.logger.debug(f'Saving user [{user.id}] to userCache.')
        self.userCache.save_entity(user)
        self.logger.info(f'Saved user [{user.id}] to userCache.')

    def load_user_cache(self, userId):
        user = self.userCache.load_entity(userId)
        if (user is None):
            self.logger.info(f'Creating user entity for user [{userId}].')
            user = UserEntity(userId)

        return user