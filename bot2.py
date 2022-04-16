#!/usr/bin/env python

from discord.ext import commands
from database import DatabaseHelper
from cmd_hands import HandsCmd
import os

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DATABASE_URL = os.getenv('DATABASE_URL') or 'postgres://postgres:1234@localhost:5432/postgres'

# docker run --rm --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=1234 -d postgres
db = DatabaseHelper(DATABASE_URL)
db.connect()
db.run_migrations()

bot = commands.Bot(command_prefix='/')
bot.db = db
bot.add_cog(HandsCmd(bot))
print('Starting bot')
bot.run(DISCORD_BOT_TOKEN)