import discord
from discord.ext import commands
from database import DatabaseHelper
from db_hands import Hands

#DOW = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
DOW = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB']

# TODO: allow per-server configuration
ROLE_TEACHER = 'Teacher'
ALLOWED_CHANNELS = ['fila-atendimento', '__teste-bot']

class HandsCmd(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.db: DatabaseHelper = bot.db

  async def check_valid_channel(self, ctx):
    if ctx.channel.name not in ALLOWED_CHANNELS:
      await ctx.message.channel.send('Use o canal #fila-atendimento')
      raise commands.CommandError('This command can only be run in fila-atendimento')

  async def check_role_teacher(self, ctx):
    user_roles = [x.name for x in ctx.author.roles]
    if ROLE_TEACHER not in user_roles:
      await ctx.message.channel.send('Você não tem permissão para usar esse comando. Digite `?h up` se quiser entrar na fila.')
      raise commands.CommandError('This command can only be run in fila-atendimento')

  @commands.group(brief='Comandos para a fila de atendimento')
  async def h(self, ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('''Comandos disponíveis para todos:

`?h up` - entra na fila de atendimento
`?h down` - sai da fila de atendimento
`?h list` - lista os usuários na fila

Comandos disponíveis para instrutores:

`?h next` - chama o próximo da fila
`?h clear` - limpa a fila''')

  @h.command(brief='Entra na fila de atendimento')
  async def up(self, ctx: commands.Context):
    await self.check_valid_channel(ctx)
    hands = Hands(self.db, ctx.message.guild.id)

    try:
      hands.up(ctx.author.id, ctx.author.display_name)
      await ctx.message.add_reaction('✅')
    except ValueError as e:
      await ctx.message.channel.send('Você já está na fila de atendimento. Aguarde a sua vez.')

  @h.command(brief='Sai da fila de atendimento')
  async def down(self, ctx: commands.Context):
    await self.check_valid_channel(ctx)
    
    hands = Hands(self.db, ctx.message.guild.id)
    hands.down(ctx.author.id)
    await ctx.message.add_reaction('✅')
  
  @h.command(brief='Chama o próximo da fila')
  async def next(self, ctx: commands.Context):
    await self.check_valid_channel(ctx)
    await self.check_role_teacher(ctx)

    hands = Hands(self.db, ctx.message.guild.id)
    user_raised = hands.next(ctx.author.id, ctx.author.display_name)
    if user_raised:
      voice_channel_text = ''
      voice_channel = ctx.author.voice
      if voice_channel is not None:
        voice_channel_text = f' no canal <#{voice_channel.channel.id}>'
      await ctx.message.channel.send(f'<@!{user_raised}>, é a sua vez! Seu atendimento será feito por **{ctx.author.display_name}**{voice_channel_text}.')
    else:
      await ctx.message.channel.send('A fila está vazia.')

  @h.command(brief='Limpa a fila')
  async def clear(self, ctx: commands.Context):
    await self.check_valid_channel(ctx)
    await self.check_role_teacher(ctx)
    
    hands = Hands(self.db, ctx.message.guild.id)
    hands.clear();
    await ctx.message.add_reaction('✅')

  @h.command(brief='Lista os usuários na fila')
  async def list(self, ctx: commands.Context):
    await self.check_valid_channel(ctx)

    hands = Hands(self.db, ctx.message.guild.id)
    await ctx.guild.chunk()
    user_ids = hands.list()
    if user_ids:
      users = [self.bot.get_user(x) for x in user_ids]
      user_list = [f'{idx + 1}: {self.bot.get_user(id=user_id).display_name} (<@!{user_id}>)' for idx, user_id in enumerate(user_ids)]
      await ctx.message.channel.send('\n'.join(user_list), allowed_mentions=discord.AllowedMentions(users=False))
    else:
      await ctx.message.channel.send('A fila está vazia.')

  @h.group(brief='Exibe estatísticas de atendimento')
  async def report(self, ctx):
    pass

  @report.command(brief='Exibe estatísticas de atendimento por instrutor')
  async def user(self, ctx):
    await self.check_role_teacher(ctx)

    hands = Hands(self.db, ctx.message.guild.id)
    l = hands.report_user()
    await ctx.guild.chunk()
    msg = ''
    for row in l:
      if row["user_id"]:
        msg += f'{row["n"]} — {self.bot.get_user(id=int(row["user_id"])).display_name} (<@{row["user_id"]}>)\n'

    if len(msg) == 0:
      msg = 'Nada a reportar'

    msg = '''Número de atendimentos por usuário:\n\n''' + msg
    await ctx.send(msg, allowed_mentions=discord.AllowedMentions(users=False))

  @report.command(brief='Exibe estatísticas de atendimento por hora do dia')
  async def hour(self, ctx):
    await self.check_role_teacher(ctx)

    hands = Hands(self.db, ctx.message.guild.id)
    l = hands.report_hour()
    msg = "Solicitações de atendimento por hora do dia:\n\n"
    if len(msg) == 0:
      msg = 'Nada a reportar'
    msg += '\n'.join([f'`{str(int(x[0])).rjust(2)}:00` => {x[1]}' for x in l])
    await ctx.send(msg)

  @report.command(brief='Exibe estatísticas de atendimento por dia da semana')
  async def day(self, ctx):
    await self.check_role_teacher(ctx)

    hands = Hands(self.db, ctx.message.guild.id)
    l = hands.report_day()
    msg = "Solicitações de atendimento por dia da semana:\n\n"
    if len(msg) == 0:
      msg = 'Nada a reportar'
    msg += '\n'.join([f'`{DOW[int(x[0])]}` => {x[1]}' for x in l])
    await ctx.send(msg)
