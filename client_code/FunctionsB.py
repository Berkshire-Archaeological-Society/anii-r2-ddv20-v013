from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
#
import re

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .. import Module1
#
from  . import Global
#

def update_status_label(self):
  """ Calculates and updates the page control row information label with the current row range."""
  page_num = int(self.table.get_page())
  rows_per_page = int(self.table.rows_per_page)
  total_rows = len(self.repeating_panel_1.items)
  # Calculate the start and end row numbers
  start_row = (page_num) * rows_per_page + 1
  end_row = min((page_num + 1) * rows_per_page, total_rows)
  # The page control buttons are not in self but in main form
  if page_num == 0:
    # disable first_page_btn and prev_page_btn if on page 0
    Global.main_form.first_page.enabled = False
    Global.main_form.prev_page.enabled = False
  else:
    Global.main_form.first_page.enabled = True
    Global.main_form.prev_page.enabled = True
  if (rows_per_page != 0) and (page_num == (total_rows // rows_per_page)):
    # disable last_page_btn and next_page_btn if on last page
    Global.main_form.last_page.enabled = False
    Global.main_form.next_page.enabled = False
  else:
    Global.main_form.last_page.enabled = True
    Global.main_form.next_page.enabled = True

  # Display the formatted string in the status label if 
  if total_rows > rows_per_page and rows_per_page != 0:
    Global.main_form.row_number_info.text = f"{start_row}-{end_row} of {total_rows}"
  else:
    # No need to display page control buttons as nr of rows is <= rows_per_page
    #print("Make all page control invisible")
    Global.main_form.last_page.enabled = False
    Global.main_form.next_page.enabled = False      
    Global.main_form.first_page.enabled = False
    Global.main_form.prev_page.enabled = False
    Global.main_form.row_number_info.text = "Total " + str(total_rows) + " rows"
  #
  Global.work_area[Global.current_work_area_name]["page_info"] = {"page_num": page_num, "rows_per_page": rows_per_page, "total_rows": total_rows}
  return

def clear_selection(self):
  # clear select checkbox of rows
  for row in self.repeating_panel_1.get_components():
    row.btn_select.checked = False
    row.background = ""

  # clear selection list
  if Global.work_area[Global.current_work_area_name].get("selected_rows") is not None:
    Global.work_area[Global.current_work_area_name]["selected_rows"].clear()

  # clear select_all checkbox
  Global.main_form.select_all.checked = False
  Global.main_form.select_all.indeterminate = False

  # make menu_select_options invisible
  Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = False
  return
  
def refresh_click(self):
  # The refresh button on the main menu has been clicked. 
  # The self variable is the one of the current_work_area_name
  # select which refresh fucntion should be called
  if Global.work_area[Global.current_work_area_name]["form_type"] == "ListUsers":
    list_users_refresh(self)
  elif Global.work_area[Global.current_work_area_name]["form_type"] == "TableList":
    table_list_refresh(self)
#  elif Global.work_area[Global.current_work_area_name]["form_type"] == "ListUsers":
#    list_anvil_users_refresh(self)
  else:
    msg = "Refresh not yet implemented."
    n = Notification(msg,timeout=Global.notification_timeout)
    n.show()
  return

def create_table_columns(column_list,work_area):
  work_area["columns_show"] = []
  columns_titles = []
  #first column is for the select button
  columns_titles.append({"id": 1, "title": "", "data_key": "select", "width": 30, "expand": False })
  id = 1
  #print("in create_table_columns: work_area[table_info] is: "+str(work_area["table_info"]))
  for column in column_list:
    # Select Column "Field"
    work_area["columns_show"].append(column)
    # work out column width on various criteria
    data_type = next(x["COLUMN_TYPE"] for x in work_area["table_info"] if x["COLUMN_NAME"] == column)
    #print("in create_table_columns: data_type is: "+data_type)
    #print(column,data_type)
    ratio = 8 # pixels per char
    padding = 10 # padding
    
    if column in Global.column_width:
      # for columns with predefined with use this
      col_width = Global.column_width[column]
    elif (data_type == "text" or ("varchar" in data_type and int(data_type.strip("varchar()")) > 50 )):
      # set width for text datatype or varchar > 50 
      col_width = 300
    elif data_type in ["date","datetime"]:
      # for date and datetime set width to max of (15 or len column name)*ratio+padding
      col_width = (max(15,len(column))) * ratio + padding
    else:
      # calculate 
      dt_len = re.findall(r'\d+', data_type)[0]
      #print("dt_len is "+str(dt_len))
      col_width = (max(int(dt_len),len(column))) * ratio + padding
    #print(column+" width is "+str(col_width))
    # do not create a columns for DBAcontrol (but for table dbdiary do create DBAcontrol column), select and for column_name with Rtf in name
    if (column == "DBAcontrol" and Global.table_name == "dbdiary") or (column not in ["select","DBAcontrol"] and column[-3:] != "Rtf"):

      id = id + 1
      columns_titles.append({"id": id, "title": column, "data_key": column, "width": col_width, "expand": True })
  
  # assign the columns titles to the grid columns
  work_area["table"].columns = columns_titles
  return
  
def table_list_refresh(self):
  # This function does the filling of the table contents
  # 1. call server function '"table_name"s_get', which retrieves all rows of the table_name for the given site
  # This only work for a true DB table refresh. If table is 'qresult' (i.e. a query result) then assign repeating_panel_1 to the Globa.table_items)
  if Global.table_name == "qresult":
    # qresult refresh is just re-pointing to Global.table_items - there is no DB table  
    self.repeating_panel_1.items = Global.table_items
  else:
    #print(Global.table_name)
    data_list = anvil.server.call("table_get",Global.site_id,Global.table_name)
    Global.col_order = data_list[1]
    self.repeating_panel_1.items = data_list[0]

  # 2. set nr of rows per page from Global variable (which is defined by a parameter in the server-side config file)
  #if Global.rows_per_page is not None:
  self.table.rows_per_page = Global.rows_per_page
  if len(self.page_info) != 0:# this means this form is called from the server (print function)
    self.table.rows_per_page = self.page_info["rows_per_page"]
    self.table.set_page(self.page_info["page_num"])

  # 3.save the list of items in the Global 'work-area' dictionary
  if Global.current_work_area_name is not None:
    Global.work_area[Global.current_work_area_name]["data_list"] = self.repeating_panel_1.items
    Global.work_area[Global.current_work_area_name]["col_order"] = Global.col_order
    
  # Trigger the initial update only if not a print action
  if not Global.print_action:
    update_status_label(self)

  clear_selection(self)
  #self.information.text = Global.table_name
  return

def list_users_refresh(self):
  # this function does the filling of the table contents
  if Global.action == "List Users":
    self.repeating_panel_1.items = anvil.server.call('system_users_get',"all")
    self.table.rows_per_page = Global.rows_per_page
    self.total_user_number.text = "Total number of Users: " + str(len(self.repeating_panel_1.items))
  elif Global.action == "List Online Users":
    self.repeating_panel_1.items = anvil.server.call('system_users_get',"online")
    self.table.rows_per_page = Global.rows_per_page
    self.total_user_number.text = "Total number of Online Users: " + str(len(self.repeating_panel_1.items))
  return

def set_select_site_dropdown_options():
  sites_list = anvil.server.call('sites_get_summary',Global.username)
  site_options = {}
  if len(sites_list) == 0:
    site_options = {"No Sites available": "No Sites Available"}
  else:
    for x in sites_list:
      val_list = list(x.values())
      option = val_list[0] + " - " + val_list[1]
      site_options[option] = val_list[0]
  return site_options

def list_anvil_users_refresh(self):
  # this function does the filling of the table contents
  self.repeating_panel_1.items = anvil.server.call('system_users_get')
  self.table.rows_per_page = Global.rows_per_page
  self.total_user_number.text = "Total number of Users: " + str(len(self.repeating_panel_1.items))
  return