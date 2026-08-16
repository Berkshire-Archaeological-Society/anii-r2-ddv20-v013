from ._anvil_designer import FilterListTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Global


class FilterList(FilterListTemplate):
  def __init__(self, options_list, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # The list of options passed from the main form
    self.repeating_panel_1.items = options_list 
    # A property to store the final selected items
    self.selected_options = [] 

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Gather all selected items from the Repeating Panel's components
    self.selected_options = [
      r.item for r in self.repeating_panel_1.get_components() 
      if r.check_box_1.checked # Assuming your item template has a Checkbox named checkbox_1
    ]

    # Raise the 'x-close-alert' event to close the popup and return the selection
    self.raise_event("x-close-alert", value=self.selected_options)
    Global.work_area[Global.current_work_area_name]["columns_show"] = []
    for col in self.selected_options:
      Global.work_area[Global.current_work_area_name]["columns_show"].append(col["text"])
    pass
