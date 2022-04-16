from discord.ext import commands
from spreadsheet_helper import SpreadsheetHelper
from db_discord_server import DiscordServer
from ss_config import ConfigSheet
from ss_student import StudentSheet

class StudentCmd(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.helper: SpreadsheetHelper = bot.spreadsheet
    self.db = bot.db

  @commands.command()
  async def checkin(self, ctx, arg=None):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    student = StudentSheet(self.helper, spreadsheet_id, config.get_config('STUDENT_WORKSHEET_NAME'))

    if arg is None:
      await ctx.message.delete()
      await ctx.send(f'Uso: /checkin numero_de_matricula')
    else:
      # TODO: improve logic in link_account
      await ctx.message.add_reaction('⌛')
      student.link_account(ctx.author.id, arg)
      await ctx.message.delete()
      await ctx.send(f'Usuário {ctx.author.display_name} vinculado ao estudante.')  # TODO: name of student

