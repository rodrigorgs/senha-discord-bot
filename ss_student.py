from collections import defaultdict

class StudentSheet:
  SHEET_STUDENTS = 'STUDENTS'
  COL_DISCORD_ID = 'DISCORD_ID'
  COL_KEY = 'STUDENT_ID'
  COL_STUDENT_ID = 'STUDENT_ID'
  COL_TEAM_ID = 'TEAM_ID'
  COL_INFO = 'INFO'

  def __init__(self, helper, spreadsheet_id):
    self.helper = helper
    self.data_table = self.helper.get_data_table(spreadsheet_id, self.SHEET_STUDENTS, self.COL_KEY, cached=False)

  def get_info(self, user_discord_id):
    user_discord_id = str(user_discord_id)
    row_with_discord_id = self.data_table.get_values_where_header_equals(self.COL_DISCORD_ID, user_discord_id)
    info = row_with_discord_id[self.COL_INFO].replace('\\n', '\n')
    return info

  def get_team(self, user_discord_id):
    user_discord_id = str(user_discord_id)
    try:
      return self.data_table.select_col_where_col_is_value(self.COL_TEAM_ID, self.COL_DISCORD_ID, user_discord_id)
    except Exception as e:
      print(e)
      return None

  def get_teams(self):
    teams = defaultdict(list)
    team_ids = self.data_table.get_values_by_header(self.COL_TEAM_ID)
    user_ids = self.data_table.get_values_by_header(self.COL_DISCORD_ID)
    for i in range(len(team_ids)):
      try:
        team_id = int(team_ids[i])
        user_id = user_ids[i]
        if user_id and len(user_id) > 0:
          teams[team_id].append(int(user_id))
      except ValueError:
        pass
      
    print('Teams: ', teams)
    return teams

  def set_team(self, user_discord_id, team_id):
    user_discord_id = str(user_discord_id)
    team_id = str(team_id)
    self.data_table.when_header_is_value_set_header_to_value(self.COL_DISCORD_ID, user_discord_id, self.COL_TEAM_ID, team_id)

  def link_account(self, user_discord_id, student_id):
    user_discord_id = str(user_discord_id)
    student_id = str(student_id)

    is_linked = True
    row_with_discord_id = None
    try:
      row_with_discord_id = self.data_table.get_values_where_header_equals(self.COL_DISCORD_ID, user_discord_id)
    except ValueError as e:
      is_linked = False

    if is_linked:
      if row_with_discord_id[self.COL_STUDENT_ID] != student_id:
        raise ValueError('Seu usuário está associado a outro número de matrícula.')
      else:
        return row_with_discord_id
    else:
      student_id_missing = False
      row_with_student_id = None
      try:
        row_with_student_id = self.data_table.get_values_by_key(student_id)
      except ValueError as e:
        student_id_missing = True
      
      if student_id_missing:
        raise ValueError('Número de matrícula inválido ou não cadastrado.')
      elif row_with_student_id[self.COL_DISCORD_ID] != '':
        raise ValueError('Esse número de matrícula está associado a outro usuário no Discord.')
      else:
        ret = self.data_table.set_value_by_key_header_and_get_row(str(student_id), self.COL_DISCORD_ID, str(user_discord_id))
        return ret
