from collections import defaultdict

class TeamSheet:
  SHEET_TEAMS = "TEAMS"
  COL_KEY = "TEAM_ID"

  def __init__(self, helper, spreadsheet_id):
    self.helper = helper
    self.data_table = self.helper.get_data_table(spreadsheet_id, self.SHEET_TEAMS, self.COL_KEY, cached=False)

  def get_attribute(self, team_id, attribute):
    team_id = str(team_id)
    row_with_team_id = self.data_table.get_values_by_key(team_id)
    return row_with_team_id[f'ATTR_{attribute}']

  def set_attribute(self, team_id, attribute, value):
    team_id = str(team_id)
    self.data_table.set_value_by_key_header(team_id, f'ATTR_{attribute}', value)
    return value