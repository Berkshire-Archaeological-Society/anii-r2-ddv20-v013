from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import re

# Global Functions
from . import Global

from ListContexts import ListContexts
from ListFinds import ListFinds
from ListSites import ListSites
from ListAreas import ListAreas
from ListUsers import ListUsers
from TableList import TableList
from ContextForm import ContextForm
from FindForm import FindForm
from AreaForm import AreaForm
from RowForm import RowForm
from SiteForm import SiteForm
from UserForm import UserForm
from ImportForm import ImportForm
from Help import Help
from Draw import Draw
#from Workarea import Workarea

def create_work_space(type,data_list):
  #print("Work space to create is: ",type)
  page_info = {}
  table_name = type.split(" ")[1].lower()
  action = type.split(" ")[0].lower()
  Global.query_view = False
  if table_name in Global.view_queries:
    Global.query_view = True

  # First param of RowForm and TableList is site_id, but is blanked out. Only used by server print function
  # Make sure any List actions that are not using the TableList Form should be listed first
  #if type in ["List Users","List Online Users"]:
  if type in ["List Users"]:
    #work_space = ListUsers()
    work_space = TableList("","users",data_list,type,page_info)
  #
  elif type in ["List Online Users"]:
    work_space = TableList("","online users",data_list,type,page_info)
  #
  elif type == "Edit User" or type == "Insert User":
    work_space = UserForm()
  #
  elif action == "list":
    work_space = TableList("",table_name,data_list,type,page_info)
  #
  elif action == "import":
    work_space = ImportForm()
  #  
  elif action == "help":
    work_space = Help()  
  #
  elif action in ["add","insert"]:
    work_space = RowForm("",table_name,data_list,type,page_info)
  #
  elif action == "edit":
    work_space = RowForm("",table_name,data_list,type,page_info)
  #
  elif action == "view":
    #print(action, table_name, type)
    if type.lower() == "view online users":
      table_name = "users"
    work_space = RowForm("",table_name,data_list,type,page_info)

  #elif type == "Draw":
  #  work_space = Draw()
  #
  elif type in ["Help Introduction","Site Introduction"]:
    work_space = Help()
  else:
    msg = "Unknown workspace to create: " + type
    #print(msg)
    work_space = "Unknown"
  return work_space

def delete_workspace(work_area_name):
  # remove work_area_name form and work_area_name button
  #print("clearing workarea : "+work_area_name)
  Global.work_area[work_area_name]["button"].remove_from_parent()
  Global.work_area[work_area_name]["form"].remove_from_parent()
  # now remove (pop) the work_area_name from lists
  Global.work_area.pop(work_area_name)
  # clear header and make it invisible
  #Global.header_work_area_name.text = ""
  #Global.header_work_area_type.text = ""
  #Global.header.visible = False
  Global.main_form.menu_bottom.visible = False
  return

def format_cell_text(text, max_chars=100):
  if not text:
   return ""

  # 1. Split into lines
  lines = text.splitlines()
  was_truncated = False

  # 2. Check for newline limit (Max 2 lines)
  # if first line is longer that half of max_chars then only take first line; otherwise take first two lines
  if len(lines[0]) > max_chars / 2:
    text_to_process = "\n".join(lines[:1])
  else:
    if len(lines) > 2:
      # Take the first two lines and mark as truncated
      # check length secnd line 
      if len(lines[1]) < max_chars / 2:
        text_to_process = "\n".join(lines[:2])
      else:
        text_to_process = lines[0] + "\n" + lines[1][:int(max_chars/2)]
      was_truncated = True
    else:
      text_to_process = "\n".join(lines)

  # 3. Check for character limit
  if len(text_to_process) > max_chars:
    # Slice it and mark as truncated
    text_to_process = text_to_process[:max_chars]
    was_truncated = True

  # 4. Apply a single ellipsis if EITHER limit was hit
  if was_truncated:
    # Strip trailing spaces/newlines so the '...' sits flush
    return text_to_process.rstrip() + "..."

  return text_to_process

def set_allowed_actions():
  # this function will set the buttons visible/invisible in the current workspace based on the access permissions on the user role for this site 
  #print("In set_allowed_actions")
  #print("Global.action: " + Global.action)
  #print("Global.current_work_area_name: " + Global.current_work_area_name)
  #print("Global.table_name: " + Global.table_name)
  #print("Global.site_user_role: " + Global.site_user_role)
  #print("Global.system_user_role: " + Global.system_user_role)
  #print("Permission: " + str(Global.role_access.get(Global.site_user_role, {}).get(Global.table_name, {}).get(Global.action.split(" ")[0], None)))
  return

def restore_workareas():
  # look for saved_workareas
  name = "Saved_areas " + Global.site_id
  rows = anvil.server.call("get_saved_workareas",name)
  for row in rows:
    for workarea in row["workarea_dict"].keys():
      #print("in restore_workares: "+row["workarea_dict"][workarea]["action"])
      Global.restore_workarea_name = workarea
      Global.table_items = row["workarea_dict"][workarea]["data_list"]
      #print (workarea)
      if row["workarea_dict"][workarea]["form_type"] == "RowForm":
        # set Global.table_items if the from_type == RowForm (View, Edit of a row) and data_list should have only one row
        Global.table_items = row["workarea_dict"][workarea]["data_list"][0]
        #print("In restore")
        #print(Global.table_items)
        #print("now calling create_new_work_area")
      if row["workarea_dict"][workarea].get("query_info") is not None:
        Global.query_info = row["workarea_dict"][workarea]["query_info"]
        #print("In restore: query_info is " + str(Global.query_info))
      if row["workarea_dict"][workarea].get("column_order") is not None:
        Global.column_order = row["workarea_dict"][workarea]["column_order"]
      if row["workarea_dict"][workarea].get("tmp_table_info") is not None:
        Global.tmp_table_info = row["workarea_dict"][workarea]["tmp_table_info"]  
        #print("In restore: tmp_table_info is " + str(Global.tmp_table_info))
      Global.main_form.create_new_work_area(row["workarea_dict"][workarea]["action"])
    Global.restore_workarea_name = ""
  return

def clean_quill_regex(html_content):
  if not html_content:
    return ""

  # Remove leading spaces after the opening <p> tag
  cleaned = re.sub(r'^(<p[^>]*>)\s+', r'\1', html_content, flags=re.IGNORECASE)

  # Remove trailing spaces before the closing </p> tag
  cleaned = re.sub(r'\s+(</p>)$', r'\1', cleaned, flags=re.IGNORECASE)

  # Remove leading/trailing empty paragraph tags (<p><br></p> or <p></p>)
  cleaned = re.sub(r'^(<p>\s*(<br/?>)?\s*</p>)+', '', cleaned, flags=re.IGNORECASE)
  cleaned = re.sub(r'(<p>\s*(<br/?>)?\s*</p>)+$', '', cleaned, flags=re.IGNORECASE)

  return cleaned.strip()