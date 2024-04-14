import datetime
import logging
import discord
from discord.ext import commands, tasks
from Utils import LeetQuery, TableCache
from Entities import ServerEntity

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=11, minute=00, tzinfo=utc)

difficultColor = {
        'easy': discord.Color.green(),
        'medium': discord.Color.yellow(),
        'hard': discord.Color.red()
        }

class DailyLC(commands.Cog):
    def __init__(self, bot, connectionString):
        self.bot = bot
        self.daily_question_loop.start()
        self.logger = logging.getLogger('discord.DailyLC')

        self.serverCache = TableCache(ServerEntity)
        self.serverCache.initialize_table(connectionString)

    def cog_unload(self):
        self.daily_question_loop.cancel()

    @tasks.loop(time=time)
    async def daily_question_loop(self):
        self.logger.debug("Preparing to send daily question.")
        await self.send_daily_question()
        self.logger.info(f'Successfully sent daily LC message.')

    async def send_daily_question(self):
            message = await self.get_daily_question_message()

            for guild in self.bot.guilds:
                try:
                    channelId = self.load_channel_cache(guild.id)
                    if (channelId > 0):
                        self.logger.info(f'Channel [{channelId}] was returned from the cache.')
                        channel = self.bot.get_channel(int(channelId))
                        if (channel is not None):
                            await channel.send(embed=message)
                            self.logger.info(f'Successfully sent daily question with link [{link}] to server [{guild.id}].')
                        else:
                            self.logger.info(f'Failed to get channel object for server [{guild.id}].')
                    else:
                        self.logger.info(f'Skip sending daily question since no channel is configured for server [{guild.id}].')
                except Exception as e:
                    # Log an error message if something goes wrong
                    self.logger.error(f"Failed to send daily question: {e}", exc_info=True)

    async def get_daily_question_message(self):
            self.logger.debug("Querying LeetCode for daily question.")

            question = await LeetQuery.daily_question()

            link = question['activeDailyCodingChallengeQuestion']['link']
            fullLink = f'https://leetcode.com{link}'

            difficulty = question['activeDailyCodingChallengeQuestion']['question']['difficulty']
            acRate = question['activeDailyCodingChallengeQuestion']['question']['acRate']
            problem = question['activeDailyCodingChallengeQuestion']['question']['title']
            isPaidOnly = question['activeDailyCodingChallengeQuestion']['question']['paidOnly']

            title = "Daily LC"
            date = datetime.datetime.now().strftime("%m-%d-%Y")
            description = f'Gooooood morning grinders. Here is your question of the day for {date}!'
            color = difficultColor[difficulty.lower()]
            fields = []
            embedMessage = discord.Embed(title=title, 
                                         description=description, 
                                         url=fullLink, 
                                         color=color)
            embedMessage.add_field(name="Problem", value=f'{problem}')
            embedMessage.add_field(name="Acceptance Rate", value=f'{acRate:.2f}%')
            embedMessage.add_field(name="Difficulty", value=f'{difficulty}')
            embedMessage.add_field(name="Is Paid Only", value=f'{isPaidOnly}')

            return embedMessage

    async def set_channel_id(self, ctx, channelId):
        channel = self.bot.get_channel(channelId)
        if channel is not None:
            self.logger.debug(f'Saving server [{str(ctx.guild.id)}] to use channel id [{channelId}].')
            self.save_channel_cache(ctx.guild.id, channelId)

            message = f'Successfully set LC bot to use channel [#{channel.name}].'
            await ctx.send(message)
            self.logger.info(message)
        else:
            message = f'Could not find channel with id [{channelId}].'
            await ctx.send(message)
            self.logger.info(message)

    def save_channel_cache(self, guildId, channelId):
        server = ServerEntity(guildId, channelId)
        self.serverCache.save_entity(server)

    def load_channel_cache(self, guildId):
        server = self.serverCache.load_entity(guildId)
        if (server is None):
            return 0

        return server.channelId
