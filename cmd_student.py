from discord.ext import commands
from spreadsheet_helper import SpreadsheetHelper
from db_discord_server import DiscordServer
from ss_config import ConfigSheet
from ss_student import StudentSheet

class StudentCmd(commands.Cog):
  COL_STUDENT_NAME = 'STUDENT_NAME'

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
      await ctx.message.add_reaction('⌛')
      
      try:
        ret = student.link_account(ctx.author.id, arg)
        student_name = ret[self.COL_STUDENT_NAME] or None
        await ctx.message.delete()
        await ctx.send(f'O usuário <@!{ctx.author.id}> foi vinculado ao estudante **{student_name}**.')
      except ValueError as e:
        await ctx.message.delete()
        await ctx.send(f'<@!{ctx.author.id}> {e}')


