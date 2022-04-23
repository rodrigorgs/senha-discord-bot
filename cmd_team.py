from discord.ext import commands
from spreadsheet_helper import SpreadsheetHelper
from db_discord_server import DiscordServer
from ss_student import StudentSheet
from ss_team import TeamSheet

class TeamCmd(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.helper: SpreadsheetHelper = bot.spreadsheet

  @commands.command(brief='Comandos para equipes')
  async def equipe(self, ctx, team_id=None, attribute=None, value=None):
    # TODO: if attribute is None, list all attributes
    if team_id is None:
      await ctx.send('''Uso: `?equipe <id da equipe> [subcomando]`''')
      return
    
    server = DiscordServer(self.bot.db, ctx.message.guild.id)
    team = TeamSheet(self.helper, server.get_spreadsheet_id())

    # TODO: escape attribute values for Discord
    try:
      if attribute is None:
        data = team.get_info(team_id)
        await ctx.send(f'''**Equipe {team_id}**:''')
        for k, v in data.items():
          await ctx.send(f'''•  **{k}**: {v}''')
      elif value is None:
        # Get attribute value
        attr_value = team.get_attribute(team_id, attribute)
        await ctx.send(f'''Equipe {team_id}: {attribute} = {attr_value}''')
      else:
        # Set attribute value (must be from team)
        student = StudentSheet(self.helper, server.get_spreadsheet_id())
        author_team = student.get_team(ctx.author.id)
        if author_team != team_id:
          await ctx.message.add_reaction('❌')
          await ctx.send(f'''Você não está na equipe {team_id}''')
          return
        attr_value = team.set_attribute(team_id, attribute, value)
        await ctx.message.add_reaction('✅')
    except KeyError:
      await ctx.message.add_reaction('❌')
      await ctx.send(f'''Atributo não encontrado: {attribute}''')