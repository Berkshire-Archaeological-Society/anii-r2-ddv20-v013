from ._anvil_designer import ListSitesTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Global

class ListSites(ListSitesTemplate):
  def list_sites_refresh(self, **event_args):
    # this function does the filling of the table contents
    #print("ListSites refresh called")
    self.SitesList.items = anvil.server.call("sites_get")
    self.Site_list_1.rows_per_page = Global.rows_per_page
    self.total_site_number.text = "Total number of Sites: " + str(len(self.SitesList.items))
  pass
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.Site_list_1.role = "horizontal-scroll"
    self.list_sites_refresh()
