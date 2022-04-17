import os
import gspread

class SpreadsheetHelper:
  def __init__(self, google_json_path):
    self.google_json_path = google_json_path
    self.gc = None
    self.init_google_client()
    self.open_spreadsheets = {}
    self.data_tables = {}

  def init_google_client(self):
    # Create JSON file to authenticate in Google Drive
    google_json_path = 'google-service-account.json'
    if not os.path.exists(google_json_path):
      with open(google_json_path, 'w') as f:
        f.write(self.google_json_path)

    # Open spreadsheet
    self.gc = gspread.service_account(filename = google_json_path)

  def get_spreadsheet(self, spreadsheet_id):
    if spreadsheet_id is None:
      raise ValueError('Empty spreadsheet id provided.')
    if spreadsheet_id not in self.open_spreadsheets:
      self.open_spreadsheets[spreadsheet_id] = self.gc.open_by_key(spreadsheet_id)
    return self.open_spreadsheets[spreadsheet_id]

  def get_data_table(self, spreadsheet_id, sheet_name, key_column_name, *, cached=False):
    index = (spreadsheet_id, sheet_name,)
    if index not in self.data_tables:
      dt = None
      if cached:
        dt = CachedDataTable(self, spreadsheet_id, sheet_name, key_column_name)
      else:
        dt = DataTable(self, spreadsheet_id, sheet_name, key_column_name)
      self.data_tables[index] = dt
    return self.data_tables[index]

class CachedDataTable:
  def __init__(self, helper, spreadsheet_id, sheet_name, key_column_name):
    self.helper = helper
    self.sheet_name = sheet_name
    self.sheet = self.helper.get_spreadsheet(spreadsheet_id).worksheet(self.sheet_name)
    self.key_column_name = key_column_name
    self.key_column_index = None
    self.data = None
    self.reload()

  def get_key_index(self, key):
    keys = self.sheet.col_values(self.key_column_index)
    return keys.index(key)

  def get_values_by_key(self, key):
    row = self.get_key_index(key)
    values = self.data[row]
    value_dict = {}
    for i in range(len(self.col_headers)):
      value_dict[self.col_headers[i]] = values[i]
    return value_dict

  def get_value_by_key_header(self, key, header):
    value_dict = self.get_values_by_key(key)
    return value_dict[header]

  def set_value_by_key_header(self, key, header, value):
    raise Exception('Not implemented yet')

  def reload(self):
    self.data = self.sheet.get_all_values()
    self.build_column_dict()

  def build_column_dict(self):
    self.column_dict = {}
    self.col_headers = self.data[0]
    for i in range(len(self.col_headers)):
      self.column_dict[self.col_headers[i]] = i + 1
    self.key_column_index = self.column_dict[self.key_column_name]

class DataTable:
  def __init__(self, helper, spreadsheet_id, sheet_name, key_column_name):
    self.helper = helper
    self.sheet_name = sheet_name
    self.sheet = self.helper.get_spreadsheet(spreadsheet_id).worksheet(self.sheet_name)
    self.key_column_name = key_column_name
    # self.build_column_dict()
    
  def build_column_dict(self):
    self.column_dict = {}
    self.col_headers = self.sheet.row_values(1)
    for i in range(len(self.col_headers)):
      self.column_dict[self.col_headers[i]] = i + 1
    self.key_column_index = self.column_dict[self.key_column_name]

  def __get_key_index(self, key):
    keys = self.sheet.col_values(self.key_column_index)
    return keys.index(key) + 1

  def __row_to_dict(self, row):
    value_dict = {}
    for i in range(len(self.col_headers)):
      value_dict[self.col_headers[i]] = row[i]
    return value_dict

  def get_values_by_header(self, header, update_index=True):
    if update_index:
      self.build_column_dict()
    col = self.column_dict[header]
    values = self.sheet.col_values(col)
    return values

  def __find_first(self, header, value):
    col_values = self.get_values_by_header(header, update_index=False)
    row_index = col_values.index(value) + 1
    return row_index

  def get_values_where_header_equals(self, header, key, update_index=True):
    if update_index:
      self.build_column_dict()
    
    row_index = self.__find_first(header, key)
    values = self.sheet.row_values(row_index)
    return self.__row_to_dict(values)

  def get_values_by_key(self, key, update_index=True):
    if update_index:
      self.build_column_dict()
    row = self.__get_key_index(key)
    values = self.sheet.row_values(row)
    return self.__row_to_dict(values)

  def get_value_by_key_header(self, key, header):
    value_dict = self.get_values_by_key(key)
    return value_dict[header]

  def set_value_by_key_header(self, key, header, value, update_index=True):
    if update_index:
      self.build_column_dict()
    row = self.__get_key_index(key)
    col = self.column_dict[header]
    self.sheet.update_cell(row, col, value)

  def when_header_is_value_set_header_to_value(self, when_header, when_value, set_header, set_value, update_index=True):
    if update_index:
      self.build_column_dict()
    row = self.__find_first(when_header, when_value)
    col = self.column_dict[set_header]
    self.sheet.update_cell(row, col, set_value)

  def set_value_by_key_header_and_get_row(self, key, header, value, update_index=True):
    if update_index:
      self.build_column_dict()
    self.set_value_by_key_header(key, header, value)
    return self.get_values_by_key(key, update_index=False)