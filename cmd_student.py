import discord
from discord.ext import commands
from spreadsheet_helper import SpreadsheetHelper
from db_discord_server import DiscordServer
from ss_student import StudentSheet
from ss_attr import AttrSheet

class StudentCmd(commands.Cog):
  COL_STUDENT_NAME = 'STUDENT_NAME'

  def __init__(self, bot):
    self.bot = bot
    self.helper: SpreadsheetHelper = bot.spreadsheet
    self.db = bot.db

  # @commands.hybrid_group(brief='Exibe equipes; há subcomandos para entrar ou sair de uma equipe', invoke_without_command=True)
  # async def equipes(self, ctx):
  #   server = DiscordServer(self.db, ctx.message.guild.id)
  #   student = StudentSheet(self.helper, server.get_spreadsheet_id())

  #   teams = student.get_teams()
  #   msg = ''
  #   await ctx.guild.chunk()
  #   for team_id in sorted(teams.keys()):
  #     user_ids = teams[team_id]
  #     # user_mentions = [f'{self.bot.get_user(int(user_id)).display_name} (<@!{user_id}>)' for user_id in user_ids]
  #     user_mentions = [f'{self.bot.get_user(int(user_id)).display_name}' for user_id in user_ids]
  #     msg += f'> **Equipe {team_id}**: ' + ', '.join(user_mentions) + '\n'

  #   if len(msg) == 0:
  #     msg = 'Nenhuma equipe encontrada.\n'
    
  #   msg += '\nDigite `?equipes entrar <id da equipe>` para entrar em uma equipe.\n'
  #   msg += '    (`<id da equipe>` é um número entre 1 e 99)\n'
  #   msg += 'Digite `?equipes sair` para sair da sua equipe.\n'

  #   am = discord.AllowedMentions(users=False,)
  #   await ctx.send(msg, allowed_mentions=am)

  # @equipes.command(brief='Sai da equipe atual')
  # async def sair(self, ctx):
  #   server = DiscordServer(self.db, ctx.message.guild.id)
  #   student = StudentSheet(self.helper, server.get_spreadsheet_id())

  #   student.set_team(ctx.message.author.id, '')
  #   await self.sync(ctx)
  #   await ctx.send('✅')

  # @equipes.command(brief='Entra em uma equipe')
  # async def entrar(self, ctx, equipe=None):
  #   try:
  #     if equipe is None:
  #       raise commands.CommandError()
  #     try:
  #       num_equipe = int(equipe)
  #       if not 1 <= num_equipe <= 99:
  #         raise commands.CommandError()
  #     except Exception:
  #       raise commands.CommandError()
  #   except commands.CommandError:
  #     await ctx.send('Uso: `?equipe entrar <equipe>`, onde <equipe> é um número de 1 a 99')
  #     return

  #   server = DiscordServer(self.db, ctx.message.guild.id)
  #   student = StudentSheet(self.helper, server.get_spreadsheet_id())

  #   equipe = str(int(equipe))    
  #   try:
  #     student.set_team(ctx.message.author.id, equipe)
  #     await self.sync(ctx)
  #     await ctx.send('✅')
  #   except ValueError:
  #     await ctx.send('Você precisa vincular seu usuário Discord a uma matrícula; para isso, use o comando `?registrar <matrícula>`')
  #     return

  # @equipes.command(brief='Sincroniza canais e cargos com equipes')
  # @commands.has_role('Teacher')
  # async def sync(self, ctx):
  #   server = DiscordServer(self.bot.db, ctx.message.guild.id)
  #   student = StudentSheet(self.helper, server.get_spreadsheet_id())

  #   # Create category
  #   try:
  #     category = [x for x in ctx.guild.categories if x.name == 'Equipes'][0]
  #   except IndexError:
  #     category = await ctx.guild.create_category('Equipes')
    
  #   await category.edit(overwrites={
  #     ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
  #   })

  #   # Get Teams
  #   teams = student.get_teams()

  #   # Create roles
  #   team_roles_current = set([r.name for r in ctx.guild.roles if r.name.startswith('Equipe')])
  #   team_roles_to_create = set([f'Equipe{id}' for id in teams.keys()]) - team_roles_current
  #   for role in team_roles_to_create:
  #     await ctx.guild.create_role(name=role)
    
  #   # Assign roles to users
  #   for team_id, students_ids in teams.items():
  #     for student_id in students_ids:
  #       user = ctx.guild.get_member(student_id)
  #       student_roles_current = set([x for x in user.roles if x.name.startswith('Equipe')])
  #       student_roles_to_add = set([x for x in ctx.guild.roles if x.name == f'Equipe{team_id}'])
  #       for role in student_roles_to_add - student_roles_current:
  #         await user.add_roles(role)
  #       for role in student_roles_current - student_roles_to_add:
  #         await user.remove_roles(role)

  #   # Create channels
  #   team_channels_current = set([c.name for c in ctx.guild.channels if c.name.startswith('equipe') and c.category == category])
  #   team_channels_to_create = set([f'equipe{id}' for id in teams.keys()]) #- team_channels_current
    
  #   teacher_role = [x for x in ctx.guild.roles if x.name == f'Teacher'][0]
  #   for channel_name in sorted(team_channels_to_create):
  #     team_id = int(channel_name.replace('equipe', ''))
  #     role = [x for x in ctx.guild.roles if x.name == f'Equipe{team_id}'][0]
  #     overwrites = {
  #       ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
  #       role: discord.PermissionOverwrite(send_messages=True, read_messages=True, view_channel=True),
  #       teacher_role: discord.PermissionOverwrite(send_messages=True, read_messages=True, view_channel=True),
  #     }
  #     # text channel
  #     if channel_name in team_channels_current:
  #       # channel = [x for x in ctx.guild.channels if x.name == channel_name and x.category == category][0]
  #       # await channel.edit(overwrites=overwrites, position=team_id)
  #       pass
  #     else:
  #       await ctx.guild.create_text_channel(channel_name, category=category, overwrites=overwrites, position=team_id)
  #     # voice channel
  #     if f'{channel_name}-voz' in team_channels_current:
  #       # channel = [x for x in ctx.guild.channels if x.name == f'{channel_name}-voz' and x.category == category][0]
  #       # await channel.edit(overwrites=overwrites, position=100 + team_id)
  #       pass
  #     else:
  #       await ctx.guild.create_voice_channel(f'{channel_name}-voz', category=category, overwrites=overwrites, position=100 + team_id)

  #   await ctx.send('✅')

  @commands.hybrid_command(brief='Obtém um dado')
  async def get(self, ctx, attr):
    server = DiscordServer(self.db, ctx.message.guild.id)
    sheet = AttrSheet(self.helper, server.get_spreadsheet_id(), StudentSheet.SHEET_STUDENTS, StudentSheet.COL_DISCORD_ID)
    try:
      await ctx.defer(ephemeral=True)
      if attr == 'all':
        value = sheet.get_all_attributes(ctx.author.id)
        info = '\n'.join([f'**{k}**: {v}' for k, v in value.items()])
      else:
        value = sheet.get_attribute(ctx.author.id, attr)
        info = f'**{attr}**: {value}'
      await ctx.send(info, ephemeral=True)
    except ValueError as e:
      # TODO: improve error reporting
      await ctx.send(f'❌ Erro', ephemeral=True)
      print(e)

  @commands.hybrid_command(brief='Altera um dado')
  async def set(self, ctx, attr, value):
    server = DiscordServer(self.db, ctx.message.guild.id)
    sheet = AttrSheet(self.helper, server.get_spreadsheet_id(), StudentSheet.SHEET_STUDENTS, StudentSheet.COL_DISCORD_ID)
    try:
      await ctx.defer(ephemeral=True)
      info = sheet.set_attribute(ctx.author.id, attr, value)
      await ctx.send(f'**{attr}**: {info}', ephemeral=True)
    except ValueError as e:
      # TODO: improve error reporting
      await ctx.send(f'❌ Erro', ephemeral=True)
      print(e)


  @commands.hybrid_command(brief='Obtém informações personalizadas sobre a disciplina')
  async def info(self, ctx):
    server = DiscordServer(self.db, ctx.message.guild.id)
    student = StudentSheet(self.helper, server.get_spreadsheet_id())
    try:
      await ctx.defer(ephemeral=True)
      info = student.get_info(ctx.author.id)
      await ctx.send(info, ephemeral=True)
    except ValueError as e:
      await ctx.send(f'❌ <@!{ctx.author.id}> Sua conta no Discord não foi vinculada a um número de matrícula. Use o comando `/registrar <matrícula>` para vincular sua conta, trocando `<matrícula>` pelo seu número de matrícula. Exemplo: `/registrar 200310593`', ephemeral=True)

  @commands.hybrid_command(brief='Vincula sua conta do Discord a um número de matrícula')
  async def registrar(self, ctx, num_matricula):
    server = DiscordServer(self.db, ctx.message.guild.id)
    student = StudentSheet(self.helper, server.get_spreadsheet_id())

    if num_matricula is None:
      await ctx.send(f'❌ Uso: `/registrar N`, onde `N` é seu número de matrícula.', ephemeral=True)
    else:
      await ctx.defer(ephemeral=True)
      
      try:
        ret = student.link_account(ctx.author.id, num_matricula)
        student_name = ret[self.COL_STUDENT_NAME] or None
        # await ctx.message.delete()
        await ctx.send(f'O usuário <@!{ctx.author.id}> foi vinculado ao estudante **{student_name}**.', ephemeral=True)
        # Send info
        info = student.get_info(ctx.author.id)
        await ctx.send(info, ephemeral=True)
      except ValueError as e:
        # await ctx.message.delete()
        await ctx.send(f'{e}', ephemeral=True)
