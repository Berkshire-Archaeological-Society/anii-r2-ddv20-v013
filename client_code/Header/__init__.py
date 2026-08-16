from ._anvil_designer import HeaderTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.media
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Global
from .. import Function

from ..TableList import TableList
from ..ListContexts import ListContexts
from ..ListFinds import ListFinds
from ..ListAreas import ListAreas
from ..ListSites import ListSites
#from ..ListUsers import ListUsers
from ..ImportForm import ImportForm
from ..FilterList import FilterList 

class Header(HeaderTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    Global.header_work_area_name = self.work_area_name
    Global.header_work_area_type = self.work_area_type
    Global.header_site_name = self.site_name
    Global.header_refresh_button = self.refresh_button
    Global.header_print_button = self.print_button
    Global.header_download_button = self.download_button
    Global.header_filter_button = self.filter_button
    Global.header_refresh_button.visible = False
    Global.header_print_button.visible = False
    Global.header_download_button.visible = False
    Global.header_filter_button.visible = False

  def work_area_name_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    # This is the work_area_name field and a new name has been enterd.
    new_work_area_name = self.work_area_name.text
    # No we need to check if it is acceptable, i.e. unique; can do the check on one of the two lists (work_area_list or work_area_name_list)
    if new_work_area_name in Global.work_area:
      # name exists, so not unique, hence name change not accepted
      alert("The new work area name is already in use. Please change it.")
    else:
      # new name is unique so now add new work area name in the two lists (one for buttons and one for the forms 
      Global.work_area[new_work_area_name] = {}
      Global.work_area[new_work_area_name] = Global.work_area[Global.current_work_area_name]
      Global.work_area[new_work_area_name]["button"].text = new_work_area_name
      
      # remove old key/value pair for the old work_area_name from the dictionaries     
      Global.work_area.pop(Global.current_work_area_name)

      # update Global.curret_work_area_name with new name
      Global.current_work_area_name = new_work_area_name
      
    pass

  def print_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    form = str(type(Global.work_area[Global.current_work_area_name]["form"])).split(".")[2][:-2]
    #print("calling print_form on server for form: ",form)
    # table name sare all lowercase and singular, so create table name from action
    tmp_name = Global.work_area[Global.current_work_area_name]["action"].split(" ")[1].strip("s")
    table_name = tmp_name.lower()
    
    # clear select column from data_list
    #i = 0
    #while i < len(Global.work_area[Global.current_work_area_name]["data_list"]):
    #  Global.work_area[Global.current_work_area_name]["data_list"][i].pop("select")
    #  i = i + 1
      
    # call the print_form at the server-side
    pdf_form = anvil.server.call('print_form',form,Global.site_id,table_name.strip(),
                                 Global.work_area[Global.current_work_area_name]["action"],
                                 Global.work_area[Global.current_work_area_name]["data_list"],
                                 Global.work_area[Global.current_work_area_name]["page_info"]
                                )
    anvil.media.download(pdf_form)
    pass

  def refresh_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # select correct refresh function to call
    #print("Refresh button clicked. Action is:", Global.work_area[Global.current_work_area_name]["action"], ", Action_form_type is: ",Global.work_area[Global.current_work_area_name]["form"])
    # select the correct refresh depending on Global.action_form_type
    if Global.work_area[Global.current_work_area_name]["action"] in ["List Contexts", "List Finds"]:
      TableList.table_list_refresh(Global.work_area[Global.current_work_area_name]["form"])
    #  ListContexts.list_contexts_refresh(Global.work_area[Global.current_work_area_name]["form"])
    #elif Global.work_area[Global.current_work_area_name]["action"] == "List Finds":
    #  ListFinds.list_finds_refresh(Global.work_area[Global.current_work_area_name]["form"])
    elif Global.work_area[Global.current_work_area_name]["action"] == "List Areas":
      ListAreas.list_areas_refresh(Global.work_area[Global.current_work_area_name]["form"])  
    elif Global.work_area[Global.current_work_area_name]["action"] == "List Sites":
      ListSites.list_sites_refresh(Global.work_area[Global.current_work_area_name]["form"]) 
    elif Global.work_area[Global.current_work_area_name]["action"] == "List Users":
      ListUsers.list_users_refresh(Global.work_area[Global.current_work_area_name]["form"]) 
    elif Global.work_area[Global.current_work_area_name]["action"] == "Import":
      ImportForm.Import_refresh(Global.work_area[Global.current_work_area_name]["form"])
    # clear list of selected_rows
    Global.work_area[Global.current_work_area_name]["selected_rows"].clear()
    pass

  def delete_work_area_click(self, **event_args):
    """This method is called when the button is clicked"""
    Function.delete_workspace(self.work_area_name.text)
    pass

  def download_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # call server-side function create_csv to create a csv file and download this to user Download folder
    csv_file = anvil.server.call('create_csv',Global.work_area[Global.current_work_area_name]["data_list"])
    anvil.media.download(csv_file)
    pass

  def filter_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    # extract table columns names
    if Global.work_area[Global.current_work_area_name]["data_list"]:
      # Get the keys (which are the column headings) from the first item
      column_headings = list(Global.work_area[Global.current_work_area_name]["data_list"][0].keys())
    
    # remove special columns
    column_headings.remove("select")
    column_headings.remove("SiteId")
    column_headings.remove("DBAcontrol")
    # sort column names
    column_headings.sort()
    
    # 1. Define the options you want to display
    option_id = 0
    options_data = []
    for column_name in column_headings:
      option_id = option_id + 1
      options_data.append({'text': column_name, 'id': option_id})

    # 2. Create an instance of your Dialog Form
    dialog = FilterList(options_list=options_data)

    # 3. Use alert() to show the form as a modal popup
    # The alert() function will return the 'value' passed when 'x-close-alert' is raised
    selected_list = alert(
      content=dialog, 
      title="",
      buttons=[] # Crucial: set buttons=[] to use your custom button for submission
    )
    if selected_list is not None:     # user has made a selection; if not, do nothing
      # 4. Process the result after the dialog is closed
      #
      # First unhide all columns
      # remove the columns out of the hidden columns list.
      for col in Global.work_area[Global.current_work_area_name]["hidden_columns"]:
        column = [c for c in Global.work_area[Global.current_work_area_name]["filter"] if c['title'] == col][0]
        # remove from list of hidden_columns
        Global.work_area[Global.current_work_area_name]["filter"].remove(column)
        # Add it to the Data Grid's column list
        Global.work_area[Global.current_work_area_name]["table"].columns.append(column)
      # make it 'live'
      Global.work_area[Global.current_work_area_name]["table"].columns = Global.work_area[Global.current_work_area_name]["table"].columns
      # set hidden_columns to empty list
      Global.work_area[Global.current_work_area_name]["hidden_columns"] = []

      #
      all_columns_titles = [col["title"] for col in Global.work_area[Global.current_work_area_name]["table"].columns if "title" in col]
      #remove columns with empty title
      cleaned_list = [item for item in all_columns_titles if item != ""]
      cleaned_list.sort()
      all_columns_titles = cleaned_list
    
      # create columns_to_hide (difference between all_columns and selected_columns)
      columns_to_hide = []
      selected_columns_titles = []
      if selected_list:
        selected_columns_titles = [col["text"] for col in selected_list if "text" in col]
        columns_to_hide = list(set(all_columns_titles).difference(selected_columns_titles))
    
      # add columns_to_hide to the work_area data structure as "filter"
      Global.work_area[Global.current_work_area_name]["hidden_columns"] = columns_to_hide
      for col in columns_to_hide:
        # add col to filter and remove from table
        column = [c for c in Global.work_area[Global.current_work_area_name]["table"].columns if c['title'] == col][0]
        Global.work_area[Global.current_work_area_name]["filter"].append(column)
        Global.work_area[Global.current_work_area_name]["table"].columns.remove(column)
    
      # make the filter 'live'
      Global.work_area[Global.current_work_area_name]["table"].columns = Global.work_area[Global.current_work_area_name]["table"].columns
    pass


    
