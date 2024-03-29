class DiscordServer:
  def __init__(self, db, discord_server_id):
    self.db = db
    self.discord_server_id = discord_server_id
    self.get_id()

  def get_id(self):
    with self.db.conn.cursor() as cur:
      cur.execute('SELECT id FROM discord_server WHERE guild_id = %s', (self.discord_server_id,))
      ret = cur.fetchone()
      if not ret:
        cur.execute('INSERT INTO discord_server(guild_id) VALUES (%s) RETURNING id', (self.discord_server_id,))
        ret = cur.fetchone()
    return ret[0]
  
  def set_spreadsheet_id(self, spreadsheet_id):
    with self.db.conn.cursor() as cur:
      cur.execute('UPDATE discord_server SET spreadsheet_id = %s WHERE guild_id = %s', (spreadsheet_id, self.discord_server_id))
      self.db.conn.commit()

  def get_spreadsheet_id(self):
    with self.db.conn.cursor() as cur:
      cur.execute('SELECT spreadsheet_id FROM discord_server WHERE guild_id = %s', (self.discord_server_id,))
      ret = cur.fetchone()
      return ret[0]