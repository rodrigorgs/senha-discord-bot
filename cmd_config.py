from discord.ext import commands
from spreadsheet_helper import SpreadsheetHelper
from db_discord_server import DiscordServer
from ss_config import ConfigSheet

class ConfigCmd(commands.Cog):
  WORKSHEET_NAME = 'BOT_CONFIG'
  COL_KEY = 'KEY'

  def __init__(self, bot):
    self.bot = bot
    self.helper: SpreadsheetHelper = bot.spreadsheet
    self.db = bot.db

  @commands.group(pass_context = True)
  async def senhaconf(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send('''TODO: implementar documentação''')

  @senhaconf.command()
  async def show(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)

    student_worksheet_name = config.get_config('STUDENT_WORKSHEET_NAME')
    await ctx.message.channel.send(f'Student worksheet: {student_worksheet_name}')

  @senhaconf.command()
  async def reload(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    config.reload()

