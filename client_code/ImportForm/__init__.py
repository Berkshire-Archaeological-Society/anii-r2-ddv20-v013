from ._anvil_designer import ImportFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media
from .. import Global

class ImportForm(ImportFormTemplate):
  def Import_refresh(self, **event_args):
    # this function does the filling of the table contents
    print("Import refresh button pressed. Current work_area ",Global.current_work_area_name )
    self.message_log.text = ""
    self.upload_file.clear()
  pass
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.Import_title.text = "Here you can import csv files for importing to the Database."
    Global.table_name = Global.action.split(" ")[1].lower()
    self.selected_table.text = Global.table_name

    Global.main_form.mb_left.visible = False
    Global.main_form.mb_middle.visible = False


  def upload_file_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    #print(Global.current_work_area_name)
    self.selected_file_name.text = ""
    self.message_log.text = ""
    Global.DBAcontrol = ""
    self.selected_file_name.text = "You have selected file: " + file.name
    msg = "You have selected file: " + file.name + "\nDo you wish to continue?"
    if confirm(content=msg):
      msg = anvil.server.call("import_file", Global.table_name, file)
      self.message_log.text = msg
      change_id = msg.splitlines(False)[0]
      #print(change_id)
      Global.DBAcontrol = change_id.split(" ")[2]
      #print(Global.DBAcontrol)
    else:
      self.upload_file.clear()
      self.selected_file_name.text = ""
      self.message_log.text = ""
    pass

  def cancel_inserts_click(self, **event_args):
    """This method is called when the button is clicked"""
    message = anvil.server.call("delete_by_DBAcontrol",Global.DBAcontrol,Global.table_name)
    self.message_log.text = self.message_log.text + message
    byte_string = bytes(self.message_log.text, "utf-8")
    text_file = anvil.BlobMedia('text/plain', byte_string, name='Import_message.log')
    anvil.media.download(text_file)
    note = "The successful inserts to table " + Global.table_name + " have been cancelled and deleted from the table. The message log has been downloaded."
    n = Notification(note)
    n.show()
    #
    self.upload_file.clear()
    self.selected_file_name.text = ""
    self.message_log.text = ""
    pass

  def commit_inserts_click(self, **event_args):
    """This method is called when the button is clicked"""
    byte_string = bytes(self.message_log.text, "utf-8")
    text_file = anvil.BlobMedia('text/plain', byte_string, name='Import_message.log')
    anvil.media.download(text_file)
    n = Notification("The successful Inserts have been comitted to the table. The message log has been downloaded.")
    n.show()
    # update Site Summary
    db_summary = anvil.server.call("db_get_summary",Global.site_id)
    Global.main_form.site_summary.visible = True
    Global.main_form.site_summary.items = db_summary
    #
    self.upload_file.clear()
    self.selected_file_name.text = ""
    self.message_log.text = ""
    pass

  @handle("download_csv_template", "click")
  def download_csv_template_click(self, **event_args):
    """This method is called when the button is clicked"""
    # need to check when using this for a query dynamic table . Cannot use the describe_table call.
    # probably need other method to get columns position to pass on to create_csv
    if Global.table_name != "users":
      table_info = anvil.server.call("describe_table",Global.table_name)
      # create empty data_list with column heading and a col_list with table ordinal_position 
      data_list = {}
      col_order = {}
      for column in table_info:
        data_list[column["COLUMN_NAME"]] = None
        col_order[column["COLUMN_NAME"]] = column["ORDINAL_POSITION"]
      #print(data_list)
      csv_name = "Template_" + Global.table_name + ".csv"
    else:
      # table users is a special case (for the Anvil users DB table)
      data_list = {"email": None, "password": None, "systemrole": None, "initials": None, "firstname": None, "lastname": None}
      col_order = {"email": 1, "password": 2, "systemrole": 3, "initials": 4, "firstname": 5, "lastname": 6}
      csv_name = "Template_system_" + Global.table_name + ".csv"
    csv_file = anvil.server.call('create_csv',[data_list],[col_order],csv_name)
    anvil.media.download(csv_file)
    pass
