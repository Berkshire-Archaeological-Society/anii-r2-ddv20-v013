from ._anvil_designer import RowTemplate3Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Global
from ... import Function

class RowTemplate3(RowTemplate3Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def view_site_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    Global.site_items = self.item
    Global.action = "View Site"
    if Global.main_form:  # Important to check if the form exists
      # Create new work_area "View Site" and set focus on this new work_area 
      Global.main_form.create_new_work_area(Global.action)
    else:
      print("Main form not found!")
    pass

  def edit_site_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    Global.site_items = self.item
    Global.action = "Edit Site"
    if Global.main_form:  # Important to check if the form exists
      # Create new work_area "Edit Site" and set focus on this new work_area 
      Global.main_form.create_new_work_area(Global.action)
    else:
      print("Main form not found!")
    pass
