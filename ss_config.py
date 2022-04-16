import gspread
from spreadsheet_helper import SpreadsheetHelper

class ConfigSheet:
  WORKSHEET_NAME = 'BOT_CONFIG'
  COL_VALUE = "VALUE"
  COL_KEY = "KEY"
  CONFIG_OPTIONS = ["STUDENT_WORKSHEET_NAME", "GROUP_WORKSHEET_NAME"]

  def __init__(self, helper, spreadsheet_id):
    self.helper = helper
    self.data_table = self.helper.get_data_table(spreadsheet_id, self.WORKSHEET_NAME, self.COL_KEY)
  
  def get_config(self, option):
    if option not in self.CONFIG_OPTIONS:
      raise Exception("Invalid option: " + option)
    
    return self.data_table.get_value_by_key_header(option, self.COL_VALUE)

