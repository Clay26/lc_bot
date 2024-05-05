# Overview
This Discord bot is designed to enhance LeetCode practice within Discord communities. It sends daily LeetCode challenges to a specified channel and tracks user progress. Users interact with the bot primarily through reactions and commands within the Discord environment.

# User Interaction
- **Daily Challenge Notification:** The bot posts a daily LeetCode problem at 11 AM UTC in a designated channel. Users can mark the challenge as completed by reacting with the ✅ emoji.
- **Tracking Progress:** Upon reacting, the bot logs the completion in a database.
- **Viewing Stats:** Users can retrieve their statistics, such as the number of easy, medium, and hard questions completed, longest streak, current streak, and today's completion status, using the `/stats` slash command.
- **Configuration:** Server admins can set the channel for daily challenges using the `?setChannel <channelId>` command.

# Local Development Setup
Follow these steps to set up your local development environment:

1. Clone the repository to your local machine.
2. Create a `.env` file in the root directory with the following content:
```
DISCORD_BOT_API_KEY='<your_discord_bot_api_key>'
STORAGE_CONNECTION_STRING='<your_azure_storage_connection_string>'
TEST_USER='<test_user_id>'
```
- **Discord Bot API Key:** Obtain from the [Discord Developer Portal](https://discord.com/developers/docs/intro).
- **Storage Connection String:** Use an Azure Storage account connection string.
- **Test User:** A user ID for testing with the ?localTest command.
3. Set up a Python virtual environment:
```
python -m venv venv
```
4. Activate the virtual environment:
- **Windows:**
```
. .\venv\Scripts\activate.ps1
```
- **macOS/Linux:**
```
source venv/bin/activate
```
5. Install dependencies:
```
pip install -r requirements.txt
```
- To update dependencies, use:
```
pip freeze > requirements.txt
```
6. Run the bot locally:
```
python lc-bot-server.py
```

# Bot Architecture
The LeetCode Discord bot operates on an Azure App Service using a Linux OS with Python 3.11 as the runtime stack. It features a minimalist Flask server hosting an `/` endpoint on port 8000, which returns "Healthy!" to signify operational status. Data is managed using Azure Storage tables that serve as caches for user statistics and channel configurations. The bot connects to this storage using a connection string provided in the `.env` file.
