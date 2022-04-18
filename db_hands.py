from datetime import datetime, timezone
from db_discord_server import DiscordServer
import threading

LOCK = threading.Lock()

class Hands:
  def __init__(self, db, guild_id):
    self.db = db
    self.guild_id = guild_id
    server = DiscordServer(self.db, guild_id)
    self.discord_server_fk = server.get_id()
  
  def up(self, user_id, user_name):
    with self.db.conn.cursor() as cur:
      cur.execute('''SELECT user_raised
        FROM hands
        WHERE user_raised = %s
          AND cleared = FALSE
          AND discord_server_id = %s''',
        (user_id, self.discord_server_fk,))
      ret = cur.fetchone()
    if ret:
      raise ValueError('Hand already up')    
    with self.db.conn.cursor() as cur:
        cur.execute('''INSERT INTO hands(
          time_raised, user_raised, user_name_raised, discord_server_id)
          VALUES (%s, %s, %s, %s)''', (datetime.now(timezone.utc), user_id, user_name, self.discord_server_fk))

  def down(self, user_id):
    with self.db.conn.cursor() as cur:
      cur.execute('''UPDATE hands
        SET cleared = TRUE
        WHERE user_raised = %s
          AND cleared = FALSE
          AND discord_server_id = %s''',
        (user_id, self.discord_server_fk,))

  # returns id of the user who raised the hands
  def next(self, caller_id, caller_name):
    try:
      LOCK.acquire()
      with self.db.conn.cursor() as cur:
        cur.execute('''SELECT user_raised
          FROM hands
          WHERE cleared = FALSE
            AND discord_server_id = %s
          ORDER BY id''',
          (self.discord_server_fk,))
        ret = cur.fetchone()
      if ret:
        user_raised_id = ret[0]
        with self.db.conn.cursor() as cur:
          cur.execute('''UPDATE hands
            SET cleared = TRUE,
              time_called = %s,
              user_called = %s,
              user_name_called = %s
            WHERE user_raised = %s
              AND cleared = FALSE
              AND discord_server_id = %s''',
            (datetime.now(timezone.utc), caller_id, caller_name, user_raised_id, self.discord_server_fk))
        return user_raised_id
      else:
        return None
        #raise ValueError('A fila está vazia.')
    finally:
      LOCK.release()

  def clear(self):
    with self.db.conn.cursor() as cur:
      cur.execute('''UPDATE hands
        SET cleared = TRUE
        WHERE cleared = FALSE
          AND discord_server_id = %s''',
        (self.discord_server_fk,))

  def list(self):
    with self.db.conn.cursor() as cur:
      cur.execute('''SELECT user_raised
        FROM hands
        WHERE cleared = FALSE
          AND discord_server_id = %s
        ORDER BY id''',
        (self.discord_server_fk,))
      ret = cur.fetchall()
      return [row[0] for row in ret]

  def report(self):
    with self.db.conn.cursor() as cur:
      cur.execute('''SELECT user_called, COUNT(*) AS n
        FROM hands
        WHERE cleared = TRUE
          AND discord_server_id = %s
        GROUP BY user_called ORDER BY n DESC''',
        (self.discord_server_fk,))
      ret = cur.fetchall()
      return [{'user_id': row[0], 'n': row[1]} for row in ret]