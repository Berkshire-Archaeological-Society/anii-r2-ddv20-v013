from ._anvil_designer import ListContextsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
from .. import Global
import anvil.server

class ListContexts(ListContextsTemplate):
  def list_contexts_refresh(self, **event_args):
    # This function does the filling of the table contents
    # 1. call server function 'context_get', which retrieves all conrtext for the given site
    self.ContextList.items = anvil.server.call("contexts_get", Global.site_id)
    self.rp.items = self.ContextList.items

    # 2. set nr of rows per page from Global variable (which is defined by a parameter in the server-side config file)
    if Global.nr_of_rows is not None:
      self.Context_list_1.rows_per_page = Global.nr_of_rows
    
    # 3.save the list of items in the Global 'work-area' dictionary
    if Global.current_work_area_name is not None:
      Global.work_area[Global.current_work_area_name]["data_list"] = self.ContextList.items
    
    # Display the total number of rows 
    self.total_context_number.text = "Total number of Contexts: " + str(len(self.ContextList.items))
  pass
  
  def __init__(self, site_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #
    self.site_id = site_id
    # Any code you write here will run before the form open
    # Global.site_id is only None when form called from server side (e.g. printing form)
    if Global.site_id is None:
      # initialise some Globals variables for server side function call
      Global.site_id = site_id
      Global.current_work_area_name = "ContextList"
      Global.work_area[Global.current_work_area_name] = {}

    # Create your Data Grid 
    self.grid = DataGrid()
    # Add the Data Grid to your Form
    self.add_component(self.grid,full_width_row=True)
    table_info = anvil.server.call("describe_table","context")
    
    # Extract the columns names from the table_info 
    # The DESCRIBE result structure is:
    # (Field:, Type:, Null:, Key:, Default:, Extra:)
    id = 0
    columns_titles = []
    for column_data in table_info:
      # Select Column Field
      field_name = column_data["Field"]
      id = id + 1
      columns_titles.append({"id": id, "title": field_name, "data_key": field_name}) 
      #'text': column_name, 'id': option_id})

    # assign the columns titles to the grid columns
    self.grid.columns = columns_titles

    # create the row structure of the datagrid
    self.rp = RepeatingPanel(item_template=DataRowPanel)
    # Set its items property

    # Add the repeating panel to your data grid and set rows_per_page
    self.grid.add_component(self.rp,full_width_row=True)
    self.grid.rows_per_page = 20
    
    Global.context_id = ""
    # refresh the table content
    self.list_contexts_refresh()




