import discord
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

  @commands.command(brief='Exibe equipes')
  async def equipes(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    student = StudentSheet(self.helper, spreadsheet_id, config.get_config('STUDENT_WORKSHEET_NAME'))

    teams = student.get_teams()
    msg = ''
    for team_id in sorted(teams.keys()):
      user_ids = teams[team_id]
      user_mentions = [f'<@{user_id}>' for user_id in user_ids]
      msg += f'**Equipe {team_id}**: ' + ', '.join(user_mentions) + '\n'

    if len(msg) == 0:
      msg = 'Nenhuma equipe encontrada.'

    am = discord.AllowedMentions(users=False,)
    await ctx.send(msg, allowed_mentions=am)

  @commands.command(brief='Sai da equipe atual')
  async def sai(self, ctx, equipe=None):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    student = StudentSheet(self.helper, spreadsheet_id, config.get_config('STUDENT_WORKSHEET_NAME'))

    student.set_team(ctx.message.author.id, '')
    await ctx.message.add_reaction('✅')

  @commands.command(brief='Entra em uma equipe')
  async def entra(self, ctx, equipe=None):
    try:
      if equipe is None:
        raise commands.CommandError()
      try:
        num_equipe = int(equipe)
        if not 1 <= num_equipe <= 20:
          raise commands.CommandError()
      except Exception:
        raise commands.CommandError()
    except commands.CommandError:
      await ctx.send('Uso: `/entra <equipe>`, onde <equipe> é um número de 1 a 20')
      return

    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    student = StudentSheet(self.helper, spreadsheet_id, config.get_config('STUDENT_WORKSHEET_NAME'))

    equipe = str(int(equipe))    
    try:
      student.set_team(ctx.message.author.id, equipe)
      await ctx.message.add_reaction('✅')
    except ValueError:
      await ctx.send('Você precisa vincular seu usuário Discord a uma matrícula; para isso, use o comando `/checkin <matrícula>`')
      return

  @commands.command(brief='Obtém informações personalizadas sobre a disciplina')
  async def info(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    student = StudentSheet(self.helper, spreadsheet_id, config.get_config('STUDENT_WORKSHEET_NAME'))
    try:
      info = student.get_info(ctx.author.id)
      await ctx.message.add_reaction('✅')
      await ctx.author.send(info)
    except ValueError as e:
      await ctx.message.add_reaction('❌')
      await ctx.send(f'<@!{ctx.author.id}> Sua conta no Discord não foi vinculada a um número de matrícula. Use o comando `/checkin` para vincular sua conta.')

  @commands.command(brief='Vincula sua conta do Discord a um número de matrícula')
  async def checkin(self, ctx, arg=None):
    server = DiscordServer(self.db, ctx.message.guild.id)
    spreadsheet_id = server.get_spreadsheet_id()
    config = ConfigSheet(self.helper, spreadsheet_id)
    student = StudentSheet(self.helper, spreadsheet_id, config.get_config('STUDENT_WORKSHEET_NAME'))

    if arg is None:
      await ctx.message.add_reaction('❌')
      await ctx.send(f'Uso: `/checkin N`, onde `N` é seu número de matrícula.')
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
