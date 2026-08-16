from ._anvil_designer import ListFindsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Global

class ListFinds(ListFindsTemplate):
  def list_finds_refresh(self, **event_args):
    # this function does the filling of the table contents
    self.FindsList.items = anvil.server.call("finds_get", Global.site_id)
    if Global.nr_of_rows is not None:
      self.Find_list_1.rows_per_page = Global.nr_of_rows
    if Global.current_work_area_name is not None:
      Global.work_area[Global.current_work_area_name]["data_list"] = self.FindsList.items
    self.total_find_number.text = "Total number of Finds: " + str(len(self.FindsList.items))
  pass
  
  def __init__(self, site_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.site_id = site_id
    # Any code you write here will run before the form opens.
    # Global.site_id is only None when form called from server side (e.g. printing form)
    if Global.site_id is None:
      # initialise some Globals variables for server side function call
      Global.site_id = site_id
      Global.current_work_area_name = "FindList"
      Global.work_area[Global.current_work_area_name] = {}
      
    Global.find_id = ""
    # refresh the table content
    self.list_finds_refresh()