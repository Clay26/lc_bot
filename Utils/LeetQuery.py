from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from typing import Optional, Dict, Any
import logging


class LeetQuery:
    logger: logging.Logger
    client: Client

    def __init__(self, url: str = "https://leetcode.com/graphql"):
        transport = AIOHTTPTransport(url=url)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

        self.logger = logging.getLogger('discord.LeetQuery')

    async def daily_question(self) -> Optional[Dict[str, Any]]:
        query = gql("""
            query questionOfToday {
              activeDailyCodingChallengeQuestion {
                date
                link
                question {
                  acRate
                  difficulty
                  frontendQuestionId: questionFrontendId
                  paidOnly: isPaidOnly
                  title
                  titleSlug
                }
              }
            }
        """)

        try:
            result = await self.client.execute_async(query)
            return result
        except Exception as e:
            self.logger.error(f"Failed to query leetcode.com for daily question: {e}", exc_info=True)
            return None
