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

  def get_data_table(self, spreadsheet_id, sheet_name, key_column_name):
    index = (spreadsheet_id, sheet_name,)
    if index not in self.data_tables:
      self.data_tables[index] = DataTable(self, spreadsheet_id, sheet_name, key_column_name)
    return self.data_tables[index]

class DataTable:
  def __init__(self, helper, spreadsheet_id, sheet_name, key_column_name):
    self.helper = helper
    self.sheet_name = sheet_name
    self.sheet = self.helper.get_spreadsheet(spreadsheet_id).worksheet(self.sheet_name)
    self.key_column_name = key_column_name
    self.build_column_dict()
    
  def build_column_dict(self):
    self.column_dict = {}
    self.col_headers = self.sheet.row_values(1)
    for i in range(len(self.col_headers)):
      self.column_dict[self.col_headers[i]] = i + 1
    self.key_column_index = self.column_dict[self.key_column_name]

  def get_key_index(self, key):
    keys = self.sheet.col_values(self.key_column_index)
    return keys.index(key) + 1

  def get_values_by_key(self, key):
    row = self.get_key_index(key)
    values = self.sheet.row_values(row)
    value_dict = {}
    for i in range(len(self.col_headers)):
      value_dict[self.col_headers[i]] = values[i]
    return value_dict

  def get_value_by_key_header(self, key, header):
    value_dict = self.get_values_by_key(key)
    return value_dict[header]

  def set_value_by_key_header(self, key, header, value):
    row = self.get_key_index(key)
    col = self.column_dict[header]
    self.sheet.update_cell(row, col, value)
