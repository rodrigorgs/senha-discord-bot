from discord.ext import commands
from spreadsheet_helper import DataTable, SpreadsheetHelper
from db_discord_server import DiscordServer
from ss_config import ConfigSheet

class ShowConfigCmd(commands.Cog):
  WORKSHEET_NAME = 'BOT_CONFIG'
  COL_KEY = 'KEY'

  def __init__(self, bot):
    self.bot = bot
    self.helper: SpreadsheetHelper = bot.spreadsheet
    self.db = bot.db

  @commands.command()
  async def showconfig(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)

    student_worksheet_name = config.get_config('STUDENT_WORKSHEET_NAME')
    await ctx.message.channel.send(f'Student worksheet: {student_worksheet_name}')


