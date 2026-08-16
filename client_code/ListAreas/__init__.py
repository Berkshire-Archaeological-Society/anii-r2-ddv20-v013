from ._anvil_designer import ListAreasTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Global

class ListAreas(ListAreasTemplate):
  def list_areas_refresh(self, **event_args):
    # this function does the filling of the table contents
    self.AreaList.items = anvil.server.call("areas_get", Global.site_id)
    self.Area_list_1.rows_per_page = Global.nr_of_rows
    self.total_area_number.text = "Total number of Areas: " + str(len(self.AreaList.items))
  pass
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    # ask the server for a list of the contexts and set nr of item per page on DataGrid (i.e. table) Context_list_1
    Global.area_id = ""
    # refresh the table content
    self.list_areas_refresh()