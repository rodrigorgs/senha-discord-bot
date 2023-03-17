class AttrSheet:
  def __init__(self, helper, spreadsheet_id, sheet, col_key):
    self.helper = helper
    self.sheet = sheet
    self.col_key = col_key
    self.data_table = self.helper.get_data_table(spreadsheet_id, self.sheet, self.col_key, cached=False)

  def get_all_attributes(self, key):
    key = str(key)
    row_with_team_id = self.data_table.get_values_where_header_equals(self.col_key, str(key))
    ret =  { k.replace('ATTR_', ''): v for k, v in row_with_team_id.items() if k.startswith('ATTR_') }
    return ret

  def get_attribute(self, key, attribute):
    key = str(key)
    row_with_team_id = self.data_table.get_values_by_key(key)
    return row_with_team_id[f'ATTR_{attribute}']

  def set_attribute(self, key, attribute, value):
    key = str(key)
    self.data_table.set_value_by_key_header(key, f'ATTR_{attribute}', value)
    return value