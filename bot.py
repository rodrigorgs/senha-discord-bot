#!/usr/bin/env python

import discord
import gspread
import psycopg2
import os
import threading
from datetime import datetime, timezone

ROLE_TEACHER = os.getenv('ROLE_TEACHER') or 'Teacher'
# Variáveis de ambiente para Discord e Google
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
# Variáveis de ambiente: colunas da planilha
COL_MATRICULA = int(os.getenv('COL_MATRICULA') or 5)
COL_NOME = int(os.getenv('COL_NOME') or 6)
COL_ID_DISCORD = int(os.getenv('COL_ID_DISCORD') or 7)
COL_NAME_DISCORD = int(os.getenv('COL_NAME_DISCORD') or 8)
COL_SENHA = int(os.getenv('COL_SENHA') or 9)
COL_ATIVO = int(os.getenv('COL_ATIVO') or 12)
VALUE_ATIVO = os.getenv('VALUE_ATIVO') or 'S'
# Database
DATABASE_URL = os.getenv('DATABASE_URL') or 'postgres://postgres:1234@db:5432/postgres'

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

# Init database
print("Connecting to " + DATABASE_URL)
conn = psycopg2.connect(DATABASE_URL) #"dbname=postgres user=postgres password=1234 host=db")
with conn.cursor() as cur:
  # Create table
  cur.execute('''CREATE TABLE IF NOT EXISTS hands (
    id SERIAL PRIMARY KEY,
    time_raised TIMESTAMP,
    user_raised TEXT,
    user_name_raised TEXT,
    time_called TIMESTAMP,
    user_called TEXT,
    user_name_called TEXT,
    cleared BOOLEAN DEFAULT FALSE
  );''')

# Thread locking
LOCK = threading.Lock()

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
  
  # private message: student asking for password
  if message.channel.type == discord.ChannelType.private:
    user_id = str(message.author.id)
    user_name = message.author.name + '#' + message.author.discriminator
    matricula = message.content.strip()

    try:
      # Busca pelo usuário
      row = busca(COL_ID_DISCORD, user_id)
      await envia_dados(message, row)
    except ValueError:
      # Busca pelo número de matrícula
      try:
        row = busca(COL_MATRICULA, matricula)
        discord_user = sheet.cell(row, COL_ID_DISCORD).value
        
        # Atualiza usuário do Discord
        if discord_user is None or len(discord_user.strip()) == 0:
          discord_user = user_id
          sheet.update_cell(row, COL_ID_DISCORD, user_id)
          sheet.update_cell(row, COL_NAME_DISCORD, user_name)
        
        # Informa senha, se usuário for correto
        if discord_user == user_id:
          await envia_dados(message, row)
        else:
          await message.channel.send(f'Esse número de matrícula está associado a outro usuário no Discord')
      except ValueError:
        await message.channel.send('Número de matrícula inválido ou não cadastrado. Digite seu número de matrícula para obter sua senha no JUDE.')
    
  else:
    # Channel message
    user_id = str(message.author.id)
    user_name = message.author.display_name
    user_roles = [x.name for x in message.author.roles]
    if message.content.startswith('?h') and not message.channel.name in ['fila-atendimento', '__teste-bot']:
      await message.channel.send('Use o canal #fila-atendimento')
    elif message.content == '?h up':  
      with conn.cursor() as cur:
        cur.execute('SELECT user_raised FROM hands WHERE user_raised = %s AND cleared = FALSE', (user_id,))
        ret = cur.fetchone()
      if ret:
        await message.channel.send('Você já está na fila de atendimento. Aguarde a sua vez.')
      else:
        with conn.cursor() as cur:
          cur.execute('INSERT INTO hands(time_raised, user_raised, user_name_raised) VALUES (%s, %s, %s)', (datetime.now(timezone.utc), user_id, user_name,))
        await message.add_reaction('✅')
    elif message.content == '?h down':
      with conn.cursor() as cur:
        cur.execute('UPDATE hands SET cleared = TRUE WHERE user_raised = %s AND cleared = FALSE', (user_id,))
      await message.add_reaction('✅')
    elif message.content == '?h next':
      if ROLE_TEACHER not in user_roles:
        await message.channel.send('Você não tem permissão para usar esse comando. Digite `?h up` se quiser entrar na fila.')
      else:
        try:
          LOCK.acquire()
          with conn.cursor() as cur:
            cur.execute('SELECT user_raised FROM hands WHERE cleared = FALSE ORDER BY id')
            ret = cur.fetchone()
          if ret:
            user_raised = ret[0]
            with conn.cursor() as cur:
              cur.execute('UPDATE hands SET cleared = TRUE, time_called = %s, user_called = %s, user_name_called = %s WHERE user_raised = %s AND cleared = FALSE', 
                  (datetime.now(timezone.utc), str(message.author.id), user_name, user_raised,))
            voice_channel_text = ''
            voice_channel = message.author.voice
            if voice_channel is not None:
              voice_channel_text = f' no canal <#{voice_channel.channel.id}>'
            await message.channel.send(f'<@!{user_raised}>, é a sua vez! Seu atendimento será feito por **{user_name}**{voice_channel_text}.')
          else:
            await message.channel.send('A fila está vazia.')
        finally:
          LOCK.release()
    elif message.content == '?h list':
      with conn.cursor() as cur:
        cur.execute('SELECT user_name_raised FROM hands WHERE cleared = FALSE ORDER BY id')
        ret = cur.fetchall()
      if ret:
        user_list = [x[0] for x in ret]
        user_enum_list = [f'{x[0] + 1}: {x[1]}' for x in enumerate(user_list)]
        await message.channel.send('```' + '\n'.join(user_enum_list) + '```')
      else:
        await message.channel.send('A fila está vazia.')
    elif message.content == '?h clear':
      if ROLE_TEACHER not in user_roles:
        await message.channel.send('Você não tem permissão para usar esse comando.')
      else:
        with conn.cursor() as cur:
          cur.execute('UPDATE hands SET cleared = TRUE WHERE cleared = FALSE')
        await message.add_reaction('✅')
    elif message.content == '?h report':
      if ROLE_TEACHER not in user_roles:
        await message.channel.send('Você não tem permissão para usar esse comando.')
      else:
        with conn.cursor() as cur:
          # cur.execute('SELECT time_raised, user_name_raised, user_name_called, time_called FROM hands WHERE cleared = TRUE ORDER BY id')
          cur.execute('SELECT user_name_called, COUNT(*) FROM hands WHERE cleared = TRUE GROUP BY user_name_called ORDER BY user_name_called')
          ret = cur.fetchall()
        if ret:
          rows = [str(x) for x in ret]
          await message.channel.send('```' + '\n'.join(rows) + '```')
        else:
          await message.channel.send('Nada a reportar.')


client.run(DISCORD_BOT_TOKEN)
