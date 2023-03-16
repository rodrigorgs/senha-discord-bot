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

  @commands.hybrid_group(brief='Configurações do bot', fallback='help')
  @commands.has_role('Teacher')
  async def unibot(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send('''Comandos disponíveis:

`?unibot set_spreadsheet_id <value>` - Define o ID da planilha do Google Drive''')

  # @unibot.command(brief='Exibe a configuração atual')
  # @commands.has_role('Teacher')
  # async def show(self, ctx):
  #   server = DiscordServer(self.db, ctx.message.guild.id)
  #   spreadsheet_id = server.get_spreadsheet_id()
  #   config = ConfigSheet(self.helper, spreadsheet_id)

  #   student_worksheet_name = config.get_config('STUDENT_WORKSHEET_NAME')
  #   await ctx.send(f'Student worksheet: {student_worksheet_name}')

  @unibot.command(brief='Define o ID da planilha do Google Drive')
  @commands.has_role('Teacher')
  async def set_spreadsheet_id(self, ctx, spreadsheet_id):
    server = DiscordServer(self.db, ctx.message.guild.id)
    server.set_spreadsheet_id(spreadsheet_id)
    await ctx.send(f'Spreadsheet ID: {spreadsheet_id}')

  @unibot.command(brief='Obtém o ID da planilha do Google Drive')
  @commands.has_role('Teacher')
  async def get_spreadsheet_id(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    await ctx.send(f'Spreadsheet ID: {spreadsheet_id}')


  # @unibot.command(brief='Recarrega as configurações a partir da planilha')
  # @commands.has_role('Teacher')
  # async def reload(self, ctx):
  #   server = DiscordServer(self.db, ctx.message.guild.id)
  #   spreadsheet_id = server.get_spreadsheet_id()
  #   config = ConfigSheet(self.helper, spreadsheet_id)
  #   config.reload()

