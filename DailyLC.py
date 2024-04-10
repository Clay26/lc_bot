import datetime
import logging
from discord.ext import commands, tasks
from LeetQuery import LeetQuery

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=12, minute=00, tzinfo=utc)


class DailyLC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channelId = None
        self.daily_question_loop.start()
        self.logger = logging.getLogger('discord.DailyLC')

    def cog_unload(self):
        self.daily_question_loop.cancel()

    @tasks.loop(time=time)
    async def daily_question_loop(self):
        self.logger.info("Preparing to send daily question.")
        await self.send_daily_question()
        self.logger.info(f'Successfully sent daily LC message on [today]')

    async def send_daily_question(self):
        try:
            self.logger.info("Querying LeetCode for daily question.")
            question = await LeetQuery.daily_question()
            link = question['activeDailyCodingChallengeQuestion']['link']
            difficulty = question['activeDailyCodingChallengeQuestion']['question']['difficulty']
            acRate = question['activeDailyCodingChallengeQuestion']['question']['acRate']
            fullLink = f'https://leetcode.com/{link}'
            message = f'Good morning grinders. Here is your question of the day: {fullLink}'
            channelId = self.channelId
            if (channelId is not None):
                channel = self.bot.get_channel(channelId)
                await channel.send(message)
                self.logger.info(f'Successfully sent daily question with link [{link}].')
            else:
                self.logger.debug("Skip sending daily question since no channel is configured")
        except Exception as e:
            # Log an error message if something goes wrong
            self.logger.error(f"Failed to send daily question: {e}", exc_info=True)

    async def set_channel_id(self, ctx, channelId):
        channel = self.bot.get_channel(channelId)
        if channel is not None:
            self.channelId = channelId
            message = f'Successfully set LC bot to use channel [#{channel.name}]'
            await ctx.send(message)
            self.logger.info(message)
        else:
            message = f'Could not find channel with id [{channelId}]'
            await ctx.send(message)
            self.logger.debug(message)
