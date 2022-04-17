class StudentSheet:
  COL_DISCORD_ID = 'DISCORD_ID'
  COL_KEY = 'STUDENT_ID'
  COL_STUDENT_ID = 'STUDENT_ID'

  def __init__(self, helper, spreadsheet_id, worksheet_name):
    self.helper = helper
    self.data_table = self.helper.get_data_table(spreadsheet_id, worksheet_name, self.COL_KEY, cached=False)

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
        