import datetime
import logging
import discord
from discord.ext import commands, tasks
from Utils import TableCache
from Entities import UserEntity


def parse_embed_fields(dailyLCFields: dict, fieldName: str) -> str:
    for field in dailyLCFields:
        if (field.name.lower() == fieldName.lower()):
            return field.value


class StatsLC(commands.Cog):
    bot: commands.Bot
    logger: logging.Logger
    userCache: TableCache

    def __init__(self, bot: commands.Bot, connectionString: str):
        self.bot = bot
        self.daily_stats_update.start()
        self.logger = logging.getLogger('discord.StatsLC')

        self.userCache = TableCache(UserEntity)
        self.userCache.initialize_table(connectionString)

    def cog_unload(self):
        self.daily_stats_update.cancel()

    @tasks.loop(time=datetime.time(hour=10, minute=58, tzinfo=datetime.timezone.utc))
    async def daily_stats_update(self):
        self.logger.debug("Preparing to update users' stats.")
        seenUserIds = set()

        for user in self.bot.get_all_members():
            if user.id in seenUserIds:
                continue
            seenUserIds.add(user.id)

            userEntity = self.load_user_cache(user.id)

            currStreak = userEntity.get_current_streak()

            if not userEntity.completedToday:
                # Reset current streak if they haven't completed today
                userEntity.currStreakStartDate = None
            else:
                if (userEntity.get_current_streak() > userEntity.longestStreak):
                    # Check if today's completion results in a new longest streak
                    userEntity.longestStreak = userEntity.get_current_streak()
                    self.logger.info(f'User [{userEntity.id}] has a new longest streak!')

            # Reset the daily completion flag for all users
            userEntity.completedToday = False

            # Save changes to the cache
            self.save_user_cache(userEntity)

        self.logger.info("Successfully updated users' stats")

    def log_user_completion(self, message: discord.Message, userId: int):
        self.logger.debug(f'Logging stats for user [{userId}].')
        userEntity = self.load_user_cache(userId)
        if (userEntity.completedToday):
            # User already completed today's question
            return
        dailyLCQuestion = message.embeds[0]

        self.increment_queston_difficulty(userEntity, dailyLCQuestion)
        self.check_streak(userEntity, message)
        self.save_user_cache(userEntity)

    def increment_queston_difficulty(self, userEntity: UserEntity, dailyLCQuestion: discord.Embed):
        difficulty = parse_embed_fields(dailyLCQuestion.fields, 'difficulty')
        if (difficulty.lower() == 'easy'):
            userEntity.numEasy += 1
        elif (difficulty.lower() == 'medium'):
            userEntity.numMedium += 1
        else:
            userEntity.numHard += 1

    def check_streak(self, userEntity: UserEntity, dailyLCMessage: discord.Message):
        now = datetime.datetime.now(datetime.timezone.utc)

        nextRelease = datetime.datetime.combine(now.date(), datetime.time(hour=11, minute=00, tzinfo=datetime.timezone.utc))

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

            if (userEntity.get_current_streak() > userEntity.longestStreak):
                # Check if today's completion results in a new longest streak
                userEntity.longestStreak = userEntity.get_current_streak()
                self.logger.info(f'User [{userEntity.id}] has a new longest streak!')

    def get_user_stats(self, user: discord.User) -> discord.Embed:
        self.logger.debug(f'Getting user [{user.id}] stats.')
        userEntity = self.load_user_cache(user.id)
        self.logger.info(f'Successfully generated user [{user.id}] stats.')
        return self.format_user_stats_embed(user.name, userEntity)

    def format_user_stats_embed(self, userName: str, userEntity: UserEntity) -> discord.Embed:
        title = f'{userName}\'s Daily LC stats'
        date = datetime.datetime.now().strftime("%m-%d-%Y")
        description = f'Here are your stats as of {date}.'
        embedMessage = discord.Embed(title=title,
                                     description=description,
                                     color=discord.Color.blue())

        embedMessage.add_field(name="Easy Solved", value=f'{userEntity.numEasy}')
        embedMessage.add_field(name="Medium Solved", value=f'{userEntity.numMedium}')
        embedMessage.add_field(name="Hard Solved", value=f'{userEntity.numHard}')
        embedMessage.add_field(name="Current Streak", value=f'{userEntity.get_current_streak()}')
        embedMessage.add_field(name="Longest Streak", value=f'{userEntity.longestStreak}')
        embedMessage.add_field(name="Completed Today's", value=f'{userEntity.completedToday}')

        return embedMessage

    def save_user_cache(self, user: discord.User):
        self.logger.debug(f'Saving user [{user.id}] to userCache.')
        self.userCache.save_entity(user)
        self.logger.info(f'Saved user [{user.id}] to userCache.')

    def load_user_cache(self, userId: int) -> UserEntity:
        user = self.userCache.load_entity(userId)
        if (user is None):
            self.logger.info(f'Creating user entity for user [{userId}].')
            user = UserEntity(userId)

        return user
