from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


class LeetQuery():
    async def daily_question():
# Select your transport with a defined url endpoint
        transport = AIOHTTPTransport(url="https://leetcode.com/graphql")

# Create a GraphQL client using the defined transport
        client = Client(transport=transport, fetch_schema_from_transport=False)

# Provide a GraphQL query
        query = gql(
            """
            query questionOfToday {
              activeDailyCodingChallengeQuestion {
                date
                userStatus
                link
                question {
                  acRate
                  difficulty
                  freqBar
                  frontendQuestionId: questionFrontendId
                  isFavor
                  paidOnly: isPaidOnly
                  status
                  title
                  titleSlug
                  hasVideoSolution
                  hasSolution
                  topicTags {
                    name
                    id
                    slug
                  }
                }
              }
            }
            """
        )

# Execute the query on the transport
        result = await client.execute_async(query)
        return result
