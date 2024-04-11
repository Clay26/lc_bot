import datetime
import logging
import json
import discord
from discord.ext import commands, tasks
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError
from LeetQuery import LeetQuery

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
        self.table_service_client = TableServiceClient.from_connection_string(conn_str=connectionString)
        self.table_name = "ChannelCache"
        self.table_client = None
        self.initialize_table()

    def cog_unload(self):
        self.daily_question_loop.cancel()

    @tasks.loop(time=time)
    async def daily_question_loop(self):
        self.logger.info("Preparing to send daily question.")
        await self.send_daily_question()
        self.logger.info(f'Successfully sent daily LC message.')

    async def send_daily_question(self):
            message = await self.get_daily_question_message()

            for guild in self.bot.guilds:
                try:
                    channelId = self.load_channel_cache(guild.id)
                    if (channelId is not None):
                        self.logger.info(f'Channel [{channelId}] was returned from the cache.')
                        channel = self.bot.get_channel(int(channelId))
                        if (channel is not None):
                            await channel.send(embed=message)
                            self.logger.info(f'Successfully sent daily question with link [{link}] to server [{guild.id}].')
                        else:
                            self.logger.debug(f'Failed to get channel object for server [{guild.id}].')
                    else:
                        self.logger.debug(f'Skip sending daily question since no channel is configured for server [{guild.id}].')
                except Exception as e:
                    # Log an error message if something goes wrong
                    self.logger.error(f"Failed to send daily question: {e}", exc_info=True)

    async def get_daily_question_message(self):
            self.logger.info("Querying LeetCode for daily question.")

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

            self.channelId = channelId
            message = f'Successfully set LC bot to use channel [#{channel.name}].'
            await ctx.send(message)
            self.logger.info(message)
        else:
            message = f'Could not find channel with id [{channelId}].'
            await ctx.send(message)
            self.logger.debug(message)

    def initialize_table(self):
        try:
            self.table_client = self.table_service_client.create_table_if_not_exists(table_name=self.table_name)
            self.logger.debug(f'Created {self.table_name} table.')
        except ResourceExistsError:
            self.table_client = self.table_service_client.get_table_client(table_name=self.table_name)
            self.logger.debug(f'Connected to {self.table_name} table.')

    def save_channel_cache(self, guild_id, channel_id):
        entity = {
            "PartitionKey": "ChannelCache",
            "RowKey": str(guild_id),
            "ChannelId": str(channel_id)
        }
        try:
            self.table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity)
        except Exception as e:
            self.logger.error(f"Error saving to Azure Table Storage: {e}")

    def load_channel_cache(self, guild_id):
        try:
            entity = self.table_client.get_entity(partition_key="ChannelCache", row_key=str(guild_id))
            self.logger.debug(f'Found server [{guild_id}] in cache!')
            return entity['ChannelId']
        except Exception:
            self.logger.debug(f'Did not find server [{guild_id}] in cache.')
            return None
