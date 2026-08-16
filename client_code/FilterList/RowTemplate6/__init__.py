from ._anvil_designer import RowTemplate6Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Global

class RowTemplate6(RowTemplate6Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.check_box_1.checked = False
    if self.item["text"] in Global.work_area[Global.current_work_area_name]["columns_show"]:
      self.check_box_1.checked = True