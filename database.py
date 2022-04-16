import psycopg2

class DatabaseHelper:
  SCHEMA_VERSION = 2

  def __init__(self, url):
    self.url = url
    self.conn = None
  
  def connect(self):
    self.conn = psycopg2.connect(self.url)
    self.conn.autocommit = True
  
  def create_tables(self):
    with self.conn.cursor() as cur:
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
      self.create_metadata_table()

  def create_metadata_table(self):
    with self.conn.cursor() as cur:
      cur.execute('''CREATE TABLE IF NOT EXISTS metadata (
        version INTEGER
      );''')
      cur.execute('''INSERT INTO metadata(version) VALUES (0);''')

  def schema_version(self):
    if self.table_exists('metadata'):
      with self.conn.cursor() as cur:
        cur.execute('''SELECT version FROM metadata;''')
        return cur.fetchone()[0]
    if self.table_exists('hands'):
      return 1
    else:
      return 0

  def table_exists(self, name):
    with self.conn.cursor() as cur:
      cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (name,))
      ret = cur.fetchone()[0]
      return ret
  
  def update_schema_to_version(self, dest_version):
    if self.schema_version() == 0:
      self.create_metadata_table()
    
    if dest_version > 0:
      for version in range(self.schema_version() + 1, dest_version + 1):
        self.migrate(version)
    else:
      raise ValueError('Invalid schema version')

  def __set_schema_version(self, version):
    with self.conn.cursor() as cur:
      cur.execute('''UPDATE metadata SET version = %s;''', (version,))

  def migrate(self, version):
    print('Migrating to version {}...'.format(version))
    if version == 1:
      with self.conn.cursor() as cur:
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
        self.create_metadata_table()
    elif version == 2:
      with self.conn.cursor() as cur:
        cur.execute('''CREATE TABLE discord_server (
          id SERIAL PRIMARY KEY,
          name TEXT,
          guild_id NUMERIC,
          spreadsheet_id TEXT
        );''')
        cur.execute('''ALTER TABLE hands
          ADD COLUMN discord_server_id INTEGER REFERENCES discord_server(id);''')
        cur.execute('''ALTER TABLE hands
          ALTER COLUMN user_raised TYPE BIGINT USING user_raised::bigint,
          ALTER COLUMN user_called TYPE BIGINT USING user_called::bigint
          ''')

    
    self.__set_schema_version(version)
    print('Done.')

  def run_migrations(self):
    self.update_schema_to_version(self.SCHEMA_VERSION)