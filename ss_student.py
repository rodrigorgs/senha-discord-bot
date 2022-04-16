class StudentSheet:
  COL_DISCORD_ID = 'DISCORD_ID'
  COL_KEY = 'STUDENT_ID'

  def __init__(self, helper, spreadsheet_id, worksheet_name):
    self.helper = helper
    self.data_table = self.helper.get_data_table(spreadsheet_id, worksheet_name, self.COL_KEY, cached=False)
    print('Class', type(self.data_table))

  def link_account(self, user_discord_id, student_id):
    self.data_table.set_value_by_key_header(str(student_id), self.COL_DISCORD_ID, str(user_discord_id))
