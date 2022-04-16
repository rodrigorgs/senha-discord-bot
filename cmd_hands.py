from discord.ext import commands
from database import DatabaseHelper
from db_hands import Hands

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

  @commands.group(pass_context = True)
  async def h(self, ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('''Comandos disponíveis para todos:

`?h up` - entra na fila de atendimento
`?h down` - sai da fila de atendimento
`?h list` - lista os usuários na fila

Comandos disponíveis para instrutores:

`?h next` - chama o próximo da fila
`?h clear` - limpa a fila''')

  @h.command()
  async def up(self, ctx: commands.Context, *, member=None):
    await self.check_valid_channel(ctx)
    hands = Hands(self.db, ctx.message.guild.id)

    try:
      hands.up(ctx.author.id, ctx.author.display_name)
      await ctx.message.add_reaction('✅')
    except ValueError as e:
      await ctx.message.channel.send('Você já está na fila de atendimento. Aguarde a sua vez.')

  @h.command()
  async def down(self, ctx: commands.Context, *, member=None):
    await self.check_valid_channel(ctx)
    
    hands = Hands(self.db, ctx.message.guild.id)
    hands.down(ctx.author.id)
    await ctx.message.add_reaction('✅')
  
  @h.command()
  async def next(self, ctx: commands.Context, *, member=None):
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

  @h.command()
  async def clear(self, ctx: commands.Context, *, member=None):
    await self.check_valid_channel(ctx)
    await self.check_role_teacher(ctx)
    
    hands = Hands(self.db, ctx.message.guild.id)
    hands.clear();
    await ctx.message.add_reaction('✅')

  @h.command()
  async def list(self, ctx: commands.Context, *, member=None):
    await self.check_valid_channel(ctx)

    hands = Hands(self.db, ctx.message.guild.id)
    ret = hands.list()
    if ret:
      user_list = [x[0] for x in ret]
      user_enum_list = [f'{x[0] + 1}: {x[1]}' for x in enumerate(user_list)]
      await ctx.message.channel.send('```' + '\n'.join(user_enum_list) + '```')
    else:
      await ctx.message.channel.send('A fila está vazia.')
