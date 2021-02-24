#!/usr/bin/env python

import discord
import gspread
import os

# Variáveis de ambiente para Discord e Google
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
# Variáveis de ambiente: colunas da planilha
COL_MATRICULA = int(os.getenv('COL_MATRICULA') or 5)
COL_NOME = int(os.getenv('COL_NOME') or 6)
COL_USUARIO_DISCORD = int(os.getenv('COL_USUARIO_DISCORD') or 7)
COL_SENHA = int(os.getenv('COL_SENHA') or 8)
COL_ATIVO = int(os.getenv('COL_ATIVO') or 11)
VALUE_ATIVO = os.getenv('VALUE_ATIVO') or 'S'

# Cria arquivo JSON para autenticar no Google Drive
google_json_path = 'google-service-account.json'
if not os.path.exists(google_json_path):
  with open(google_json_path, 'w') as f:
    f.write(GOOGLE_SERVICE_ACCOUNT_JSON)

# Abre planilha
gc = gspread.service_account(filename = google_json_path)
sheet = gc.open_by_key(SPREADSHEET_ID).get_worksheet(0)

# Define bot
client = discord.Client()

@client.event
async def on_ready() :
  await client.change_presence(status = discord.Status.idle, activity = None)
  print("I am online")

def busca(coluna, valor):
  values = sheet.col_values(coluna)
  row = 1 + values.index(valor)
  if row == 1:
    raise ValueError
  
  return row

async def envia_dados(message, row):
  value_ativo = sheet.cell(row, COL_ATIVO).value
  ativo = value_ativo is not None and value_ativo.strip().upper() == VALUE_ATIVO.upper()
  login = 'a' + sheet.cell(row, COL_MATRICULA).value
  nome = sheet.cell(row, COL_NOME).value
  senha = sheet.cell(row, COL_SENHA).value

  if ativo:
    await message.channel.send(f'Olá, {nome}!\n\nSeguem seus dados para acesso ao JUDE:\n\n**Endereço**: http://200.128.51.30/\n**Login**: {login}\n**Senha**: {senha}')
  else:
    await message.channel.send(f'Olá, {nome}!\nVocê ainda não foi cadastrado(a) no JUDE. Tente novamente em outro momento.')

@client.event
async def on_message(message):
  # don't respond to ourselves
  if message.author == client.user:
    return
  # don't respond to channel messages
  if message.channel.type != discord.ChannelType.private:
    return

  user_id = message.author.name + '#' + message.author.discriminator  #str(message.author.id)
  matricula = message.content.strip()

  try:
    # Busca pelo usuário
    row = busca(COL_USUARIO_DISCORD, user_id)
    await envia_dados(message, row)
  except ValueError:
    # Busca pelo número de matrícula
    try:
      row = busca(COL_MATRICULA, matricula)
      discord_user = sheet.cell(row, COL_USUARIO_DISCORD).value
      
      # Atualiza usuário do Discord
      if discord_user is None or len(discord_user.strip()) == 0:
        discord_user = user_id
        sheet.update_cell(row, COL_USUARIO_DISCORD, discord_user)
      
      # Informa senha, se usuário for correto
      if discord_user == user_id:
        await envia_dados(message, row)
      else:
        await message.channel.send(f'Esse número de matrícula está associado a outro usuário no Discord')
    except ValueError:
      await message.channel.send('Número de matrícula inválido ou não cadastrado. Digite seu número de matrícula para obter sua senha no JUDE.')

client.run(DISCORD_BOT_TOKEN)