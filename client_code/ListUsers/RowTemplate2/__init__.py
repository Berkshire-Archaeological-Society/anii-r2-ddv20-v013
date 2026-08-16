from ._anvil_designer import RowTemplate2Template
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Global
from ... import Function
from ... import FunctionsB

class RowTemplate2(RowTemplate2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.delete_user_button.visible = False
    self.edit_user_button.visible = False
    #print(Global.login_system_user_role)
    if Global.login_system_user_role == "System Administrator":
      self.delete_user_button.visible = True
      self.edit_user_button.visible = True

  def edit_user_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    Global.user_items = self.item
    Global.action = "Edit User"
    if Global.main_form:  # Important to check if the form exists
      # Create new work_area "Edit User" and set focus on this new work_area 
      Global.main_form.create_new_work_area(Global.action)
    else:
      print("Main form not found!")
  pass

  @handle("delete_user_button", "click")
  def delete_user_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    Global.user_items = self.item
    Global.action = "Delete User"
    if Global.main_form:  # Important to check if the form exists
      #print(Global.user_items)
      if confirm(f"Do you really want to delete the user {Global.user_items['email']}?"):
        anvil.server.call('system_user_delete', Global.user_items)
        #refresh the Data Grid
        FunctionsB.list_users_refresh(Global.work_area[Global.current_work_area_name]["self"])
    else:
      print("Main form not found!")
  pass
