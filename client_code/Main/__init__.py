from ._anvil_designer import MainTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from anvil.js.window import document
import anvil.js
from anvil.js import window

from .. import indeterminate
from ..Header import Header
from ..RowForm import RowForm
from ..TableList import TableList
from ..ImportForm import ImportForm
from ..FilterList import FilterList
from .. import Global
from .. import Function
from .. import FunctionsB
from ..Help import Help

# branch V054

class Main(MainTemplate):  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #
    self.last_server_update = 0
    # Any code you write here will run before the form opens.
    # get client variable settings from server configuration file
    globals_from_config = anvil.server.call("client_globals")
    Global.rows_per_page = globals_from_config["rows_per_page"]
    Global.version = globals_from_config["version"]
    Global.organisation = globals_from_config["organisation"]
    Global.config_version = globals_from_config["version"]
    Global.admin_domain = globals_from_config["admin_domain"]
    Global.db_name = globals_from_config["db_name"]
    Global.admin_domain = globals_from_config["admin_domain"]
    Global.admin_user = globals_from_config["admin_user"]
    Global.admin_user_initials = globals_from_config["admin_user_initials"]
    Global.prefix_special_finds_table = globals_from_config["prefix_special_finds_table"]

    Global.selected_highlight_colour = globals_from_config["highlight_colour"]
    
    # set the title of a browser tab to be system (which is application name Anchurus-II R2 ) + organisation name (which is realy the anchurus system name)
    document.title = Global.system + "-" + Global.organisation

    # add Header component (but make it invisible)
    #Global.header = Header()
    #self.add_component(Global.header, slot='header_slot')
    #Global.header.visible = False
    # add Help component (but make it invisible)
    #Global.help_page = Help()
    #self.add_component(Global.help_page, slot='help_slot')
    #Global.help_page.visible = False

    # set Main title field with name of organisation (defined in Anchurus-2.cgf file from server)
    #Global.title_label = self.title
    #self.title.text = Global.title + Global.status + Global.selected_site
    self.app_title.text = Global.system
    self.organisation.text = Global.organisation
    self.app_title.text = Global.system
    self.organisation.text = Global.organisation
    self.app_name.text = document.head.querySelector('[name=title]').content
    self.config_version.text = "cfg " + Global.config_version
    self.db_name.text = Global.db_name

    # Update last_seen on page load
    self.refresh_online_count()
    
    # add the about_us_text (taken from Anchurus-2.cfg file) to the about_us_box text field by adding a Rich Text Component
    rt = RichText(content=Global.about_us_text,format="restricted_html")
    self.about_us_box.add_component(rt)
    
    # Create empty work_area_list
    Global.work_area_list = {}

    # Get table list and create dropdown options for list and insert
    table_list = anvil.server.call("db_table_list")    
    Global.insert_action_dropdown = table_list
    Global.list_action_dropdown = table_list
    Global.import_action_dropdown = table_list
    # fill action menu options
    self.import_dropdown.items = Global.import_action_dropdown
    self.insert_dropdown.items = Global.insert_action_dropdown
    self.list_dropdown.items = Global.list_action_dropdown
    self.admin_dropdown.items = Global.sys_admin_action_dropdown
    #self.query_dropdown.items = Global.query_action_dropdown
    #self.file_dropdown.items = Global.file_list
    #self.view_dropdown.items = Global.view_action_dropdown
    self.help_dropdown.items = Global.help_action_dropdown
    #
    #self.file_dropdown.items = Global.file_action_dropdown

    #self.action_list.items = Global.user_action_list
    # make all fields invisible to only show about_us_text box as welcome followed by login and registration buttons (see design of Main)
    Global.wa_header_menu_bottom = self.menu_bottom
    Global.wa_header_mb_left = self.mb_left
    Global.wa_header_mb_middle = self.mb_middle
    Global.wa_header_mb_search = self.mb_search
    Global.wa_header_mb_right = self.mb_right
    #self.action_list.visible = False
    self.site_summary.visible = False
    #
    self.menu_block.visible = True
    self.title_panel.visible = True
    self.menu_top.visible = False
    self.menu_middle.visible = False
    #self.mm_left.visible = False
    #self.mm_right.visible = False
    #
    Global.wa_header_menu_bottom.visible = False
    #
    self.admin_dropdown.visible = False
    Global.main_form = self

  #
  # Functions
  # =========
  def work_area_click(self, **event_args):
    """" This function is called when the work area button is clicked. Here we make sure all the variable are set correct for the work area swap"""
    # Here the user clicked on a work_area button in the left navigation list, requested to go to a different work area.
    # first make all work_areas invisible and set button to be 'normal', i.e. not highlighted
    for name in Global.work_area:
      Global.work_area[name]["form"].visible = False
      Global.work_area[name]["button"].bold = False
      Global.work_area[name]["button"].background = Global.button_normal_background_clour
    
    # now get the name of the button (work_area_name) that was clicked and make this and the associated work_area visible

    # full workspace name is in tooltip, strip first 17 chars ("select workspace")
    work_area = event_args['sender'].tooltip[17:]
    #print("Clicked workspace ",work_area)
    Global.current_work_area_name = work_area

    # check if CTRL key was pressed when clicked. This is a workaround to use CTRL/Click to delete a workspace
    if event_args["keys"]["ctrl"]:
      # delete workspace when CTRL is pressed when workspace clicked 
      Function.delete_workspace(Global.current_work_area_name)
    else:
      # normal Click: make this workspace the current workspace
      # Set Global.table_name linked with work_area_type
      Global.table_name = Global.work_area[Global.current_work_area_name]["action"].split(" ",1)[1].lower()

      # set Global variables for site information
      Global.site_name = Global.work_area[Global.current_work_area_name]["site_name"]
      Global.site_id = Global.work_area[Global.current_work_area_name]["site_id"]
      Global.selected_site = ": " + Global.site_name
    
      # Fill header fields with work_area name and work_area Form name
      # This was for old header, can prob removed
      #Global.header_work_area_name.text = Global.current_work_area_name
      #Global.header_work_area_type.text = str(type(Global.work_area[Global.current_work_area_name]["form"])).split(".")[2][:-2]
      #Global.header_site_name.text = Global.work_area[Global.current_work_area_name]["site_name"]

      # Show work_area and set focus on work_area_name
      Global.work_area[Global.current_work_area_name]["form"].visible = True
      Global.work_area[Global.current_work_area_name]["button"].bold = False
      Global.work_area[Global.current_work_area_name]["button"].background = Global.button_highlight_background_clour

      # make old header invisible
      #Global.header.visible = False
      Global.wa_header_menu_bottom.visible = True
    
      # set menu_select_options as invisible
      Global.work_area[Global.current_work_area_name]["menu_select_options"] = self.fp_select_options
      Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = False

      Global.action_form_type = str(type(Global.work_area[Global.current_work_area_name]["form"])).split(".")[2][:-2]
      
      #print("Work area action form type: ",Global.action_form_type)
      if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["View", "Edit", "Insert", "Add", "Import"]:
      #if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["View", "Edit", "Insert", "Add", "Import"] or Global.work_area[Global.current_work_area_name]["action"] == "List Users":
      #if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["View", "Edit", "Insert", "Add", "Import"]:
        self.mb_middle.visible = False
        self.mb_search.visible = False
        self.mb_left.visible = False
      elif Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["List"]:
        self.mb_middle.visible = True
        self.mb_search.visible = True
        self.mb_left.visible = True

      self.select_all.indeterminate = False
      self.select_all.checked = False

      # update status label (page control information) if work_space is a List 
      #if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["List"] and Global.work_area[Global.current_work_area_name]["action"] != "List Users":
      if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["List"]:
        #print(Global.current_work_area_name)
        FunctionsB.update_status_label(Global.work_area[Global.current_work_area_name]["self"])

      if len(Global.work_area[Global.current_work_area_name]["selected_rows"]) == 0:
        #print("work_area_click: ", Global.current_work_area_name, " 0 selected rows, disable menu")
        Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = False
        self.select_all.checked = False
        self.select_all.indeterminate = False
        #Global.work_area[Global.current_work_area_name]["self"].select_all
      else:
        #print("work_area_click: ", Global.current_work_area_name, " there are selected rows, enable menu")
        Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = True
        page_num = int(Global.work_area[Global.current_work_area_name]["table"].get_page())
        rows_per_page = int(Global.work_area[Global.current_work_area_name]["table"].rows_per_page)
        total_rows = len(Global.work_area[Global.current_work_area_name]["self"].repeating_panel_1.items)
        rest = total_rows - page_num * rows_per_page
        #print(str(len(Global.work_area[Global.current_work_area_name]["selected_rows"])),str(rest),str(Global.rows_per_page))
        if str(len(Global.work_area[Global.current_work_area_name]["selected_rows"])) == str(Global.rows_per_page) or str(len(Global.work_area[Global.current_work_area_name]["selected_rows"])) == str(rest):
          self.select_all.checked = True 
        else:
          self.select_all.indeterminate = True
    
      #self.select_all.checked = Global.work_area[Global.current_work_area_name]["self"].select_all.checked
      #self.select_all.indeterminate = Global.work_area[Global.current_work_area_name]["self"].select_all.indeterminate

      # Set selected buttons on Header for work area type
      #print(Global.table_name)
      if Global.action_form_type in Global.action_forms_with_refresh:
        # Make refresh button visible for Global.action_form_type
        # do not do this for users table
        #self.refresh.visible = True if Global.table_name != "users" else False
        # no refresh for View  and Edit and not for qresult
        self.refresh.visible = True if Global.table_name not in ["qresult"] and Global.work_area[Global.current_work_area_name]["action"].split(" ")[0].lower() not in ["view","edit"] else False

      else:
        #Global.header_refresh_button.visible = False
        self.refresh.visible = False
      if Global.action_form_type in Global.action_forms_with_print:
        # Make print button visible for Global.action_form_type
        #Global.header_print_button.visible = True
        self.print.visible = True
      else:
        #Global.header_print_button.visible = False
        self.print.visible = False
      if Global.action_form_type in Global.action_forms_with_download:
        # Make download button visible for Global.action_form_type
        #Global.header_download_button.visible = True
        self.download_csv.visible = True if Global.table_name != "users" and Global.login_site_user_role != "Site Viewer" else False
      else:
        #Global.header_download_button.visible = False
        self.download_csv.visible = False
      if Global.action_form_type in Global.action_forms_with_filter and Global.work_area[Global.current_work_area_name]["data_list"]:
        # Make filter button visible for Global.action_form_type if data_list is not empty
        #Global.header_filter_button.visible = True
        self.filter_cols.visible = True if Global.table_name  not in ["users","qresult","query"] else False
      else:
        #Global.header_filter_button.visible = False
        self.filter_cols.visible = False
      #print(Global.work_area[Global.current_work_area_name].keys())
      #print(Global.work_area[Global.current_work_area_name]["data_list"])
      # be carefull: not all work_ara have the table
      #print(Global.work_area[Global.current_work_area_name]["table"])

      # set edit_row and delete_row visibilty that were saved in create workspace
      self.view_row.visible = Global.work_area[Global.current_work_area_name]["visibility_view_row"]
      self.edit_row.visible = Global.work_area[Global.current_work_area_name]["visibility_edit_row"]
      self.delete_row.visible = Global.work_area[Global.current_work_area_name]["visibility_delete_row"] 
      self.execute_sql.visible = Global.work_area[Global.current_work_area_name]["visibility_execute_sql"] 

      #
      #print("In work_area_click")
      table = Global.table_name
      if Global.table_name[0:2] == Global.prefix_special_finds_table:
        table = "fs tables"
      role = "System Administrator"
      if Global.login_system_user_role == "Site User":
        role = Global.login_site_user_role
      #print(role)
      #print(table)
      self.edit_row.visible = Global.role_access.get(role, {}).get(table, {}).get("Edit", None)
      self.delete_row.visible = Global.role_access.get(role, {}).get(table, {}).get("Delete", None)
      #print("set edit_row: " + str(self.edit_row.visible))
      #print("set delete_row: " + str(self.delete_row.visible))
  pass # work_area_click

  def create_new_work_area(self,action):
    """ This Function is called when a user creates a new work area"""
    #
    # First make sure the old header is invisible
    #print("In create_new_work_area")
    #print("Global.site_user_role: " + Global.site_user_role)
    #print("Global.system_user_role: " + Global.system_user_role)
    #Global.header.visible = False
    Global.wa_header_menu_bottom.visible = True
    Global.action = action
    
    # set name of work_area to be action name with small modifications in some cases
    work_area_name = action.capitalize()
    if action in ["List Users","Insert User","Import Users"]:
      work_area_name = action.split(" ")[0] + " System " + action.split(" ",1)[1]
    if action.split(" ",1)[1].lower() == "siteuserrole":
      work_area_name = action.split(" ")[0] + " Site User"
      if action.split(" ")[0] != "Insert":
        work_area_name = work_area_name + "s"   
      
    if action.lower() in ["list online users","view online users"]:
      Global.table_name = "online users"
    else:
      Global.table_name = action.split(" ",1)[1].lower()
    table_info = [] 
    
    if action == "Help Introduction":
      work_area_name = "Introduction"
    else:
      # get table_info, works only for a true DB table. If not (e.g. table is 'qresult') we have to create the table_info dictionary list ourselves   
      if Global.table_name != "qresult":
        # get the Table information form the Database
        #print(Global.table_name)
        table_info = anvil.server.call("describe_table", Global.table_name)
        #print(table_info)
        Global.query_view = False
      else:
        Global.query_view = True
        # Build the table_info structure froom the "describe table_info" from the execute_sql_command call saved in Global.tmp_table_info
        tmp_table_info = []
        #print("in create_new_work_area: column_order is "+str(Global.column_order))
        for col in Global.column_order:
          # loop through columns of first row table_item
          #print("in create_new_work_area: col is "+str(col))
          col_info = {}
          col_info["COLUMN_NAME"] = col
          # Global.tmp_table_info already a list not need to use list(Global.tmp_table_info)
          #for item in Global.tmp_table_info:
            #print("in create_new_work_area: item of temp_table_info is "+str(item))
          col_info["COLUMN_TYPE"] = next((str(item["Type"]) for item in Global.tmp_table_info if item["Field"] == col),0)
          col_info["COLUMN_KEY"] = next((str(item["Key"]) for item in Global.tmp_table_info if item["Field"] == col),0)
          col_info["IS_NULLABLE"] = next((str(item["Null"]) for item in Global.tmp_table_info if item["Field"] == col),0)
          col_info["COLUMN_DEFAULT"] = next((str(item["Default"]) for item in Global.tmp_table_info if item["Field"] == col),0)
          col_info["CHARACTER_MAXIMUM_LENGTH"] = 65535
          col_info["COLUMN_COMMENT"] = ""
          col_info["ORDINAL_POSITION"] = Global.column_order[col]
          #print(col_info)
          tmp_table_info.append(col_info)
        # sort table_info in ORDINAL_POSITION
        table_info = sorted(tmp_table_info, key=lambda x: x['ORDINAL_POSITION'])
      
    ###
    # check is we are restoring work_areas (if so use that name for work_area_name)
    if Global.restore_workarea_name == "":
      # For all actions not in Admin_action_list check ID field for creating unique work_area name
      #print(action)
      if action not in Global.sys_admin_action_list and action not in Global.site_admin_action_list and action.lower() not in ["list qresult","list qresult","view query","edit query","help introduction","site introduction"]:
        # 
        # trying to make a work_area_name suitabe for action and table (i.e. (List |[E|V]-|Insert )<table_name> <main-pri_id>)
        # add first Primary Key ID field when view or edit
        primary_key_list = []
        #print(action)
        if action.split(" ",1)[1].lower() == "dbdiary":
          primary_key_list.append("DBAcontrol")
        elif action.split(" ",1)[1].lower() == "users":
          primary_key_list.append("email")
        #elif action.split(" ",1)[1].lower() == "qresult":
        #  primary_key_list.append("QueryId")
        else:
          for column in table_info:
            if column["COLUMN_KEY"] == "PRI":
              primary_key_list.append(column["COLUMN_NAME"])
        if action.split(" ")[0].lower() in ["view","edit"]:
          work_area_name = ""
          if action.split(" ",1)[1].lower() != "dbdiary":
            if action.split(" ")[0].lower() ==  "view":
              work_area_name = "V-"
            else:
              work_area_name = "U-"
          if action.split(" ",1)[1].lower() == "siteuserrole":
            work_area_name = work_area_name + action.split(" ",1)[1][-8:]
          else:
            work_area_name = work_area_name + action.split(" ",1)[1]
          if len(primary_key_list) > 0:
            if len(primary_key_list) == 1:
              work_area_name = work_area_name + " " + Global.table_items[primary_key_list[0]]
            else:
              work_area_name = work_area_name + " " + Global.table_items[primary_key_list[1]]
      # for List Qresult we add the QueryId
      if action == "View Qresult":
        #print("in creating work area name; action is View Qresult. Checking QueryId "+Global.query_id)
        work_area_name = work_area_name + " " + Global.query_id
      if action.lower() in ["list qresult","view query","edit query"]:
        # problem with restore workarea
        if action.split(" ")[0] in ["View", "Edit"]:
          Global.query_id = Global.table_items["QueryId"]
          #print(Global.query_id)
        work_area_name = work_area_name + " " + Global.query_id
    else:
      # in restore workareas use the work_area_name of the saved work_area
      work_area_name = Global.restore_workarea_name
      
    # check if work_area_name exists and keep counter
    if (Global.work_area.get(work_area_name) is None):
      if Global.action_seq_no.get(work_area_name) is None:
        # only set seq_no to 1 if the work_area_name has never been used before 
        Global.action_seq_no[work_area_name] = 1
      else:
        # this is for increasing the counter eventhough the work_area_name is not in use.
        # this code will cater if there have already been instances of work_area_name but 'earlier' ones have been deleted.
        Global.action_seq_no[work_area_name] += 1
        work_area_name = work_area_name + " (" + str(Global.action_seq_no[work_area_name]) + ")"
    else:
      # work_area_name exists, so update work_area_name to add seq_no in brackets
      Global.action_seq_no[work_area_name] += 1
      work_area_name = work_area_name + " (" + str(Global.action_seq_no[work_area_name]) + ")"

    # create new 'empty row' in nested work_area dictionary for the new work_area_name
    Global.work_area[work_area_name] = {}
    Global.work_area[work_area_name]["action"] = action
    Global.current_work_area_name = work_area_name
    
    # save table_info in work_area structure
    Global.work_area[work_area_name]["table_info"] = table_info
    Global.work_area[work_area_name]["column_order"] = Global.column_order
    Global.work_area[work_area_name]["tmp_table_info"] = Global.tmp_table_info
    # save the query_info (row selected with the QueryId)
    Global.work_area[Global.current_work_area_name]["query_info"] = Global.query_info
    
    # set menu_select_opti0ns as invisible
    Global.work_area[Global.current_work_area_name]["menu_select_options"] = self.fp_select_options
    Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = False
  
    # create the button for the work_area in the navigation panel, add it to the work_area_list Column Panel and set event handler for when clicked
    if Global.dummy_btn1 != {}:
      Global.dummy_btn1.remove_from_parent() 
      Global.dummy_btn2.remove_from_parent() 

    #limit button text to first limit_workspace_name_btn_text chars and set tooltip to shown full text
    tooltip_text = "select workspace " + work_area_name
    limit_workspace_name_btn_text = 25
    Global.work_area[work_area_name]["button"] = Button(text=work_area_name[:limit_workspace_name_btn_text],align="left",tooltip=tooltip_text)
    Global.work_area[work_area_name]["button"].role = "primary-color"
    self.work_area_list.add_component(Global.work_area[work_area_name]["button"])
    Global.work_area[work_area_name]["button"].add_event_handler('click', self.work_area_click)
    
    Global.dummy_btn1 = Button(text="")
    Global.dummy_btn1.enabled = False
    Global.dummy_btn1.visible = True
    self.work_area_list.add_component(Global.dummy_btn1) 
    Global.dummy_btn2 = Button(text="")
    Global.dummy_btn2.enabled = False
    Global.dummy_btn2.visible = True
    self.work_area_list.add_component(Global.dummy_btn2)
    
    # add the Global.table_items to the work_area_name - not for "insert" action
    if action.split(" ",1)[0].lower() != "insert":
      Global.work_area[work_area_name]["data_list"] = [Global.table_items]
    
    # create a new work_space and add this to the work_area_list and add component to main     
    #print("Main create_new_work_area: ",self)
    #print("Call to create_work_space "+action)
    form_result = Function.create_work_space(action,Global.table_items)
    if form_result != "Unknown":
      #print(action, work_area_name, Global.work_area)
      Global.work_area[work_area_name]["form"] = form_result
      #print(Global.work_area[work_area_name]["form"])
      self.add_component(Global.work_area[work_area_name]["form"])
       
      # set button name to new work_area_name (limit to first limit_workspace_name_btn_text chars - tooltip shows full name)
      Global.work_area[work_area_name]["button"].text = work_area_name[:limit_workspace_name_btn_text]
      Global.work_area[work_area_name]["form_type"] = str(type(Global.work_area[work_area_name]["form"])).split(".")[2][:-2]
      #
      Global.work_area[work_area_name]["site_name"] = Global.site_name
      #Global.header_site_name.text = Global.work_area[work_area_name]["site_name"]
      Global.work_area[work_area_name]["site_id"] = Global.site_id
    
      # set selected rows list to empty
      Global.work_area[work_area_name]["selected_rows"] = []

      # make all work spaces invisible
      for name in Global.work_area:
        Global.work_area[name]["form"].visible = False
        Global.work_area[name]["button"].bold = False
        Global.work_area[name]["button"].background = Global.button_normal_background_clour
    
      # create an empty filter and empty hidden_columns
      Global.work_area[Global.current_work_area_name]["filter"] = []
      Global.work_area[Global.current_work_area_name]["hidden_columns"] = []
    
      # Make newly created work area visible and have Focus
      Global.work_area[work_area_name]["form"].visible = True
      Global.work_area[work_area_name]["button"].bold = False
      Global.work_area[work_area_name]["button"].background = Global.button_highlight_background_clour
      #
      #Global.header_work_area_name.text = work_area_name
      Global.current_work_area_name = work_area_name
      #Global.header_work_area_type.text = str(type(Global.work_area[Global.current_work_area_name]["form"])).split(".")[2][:-2]
      #Global.header_work_area_type.enabled = False
      #print(Global.header_work_area_type.text)
      Global.action_form_type = Global.work_area[work_area_name]["form_type"]
      #Global.action_form_type = Global.header_work_area_type.text.split(".")[2][:-2]
      #Global.action_form_type = Global.header_work_area_type.text
      #
      # Only show page controls for List Table action
      if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["View", "Edit", "Insert", "Add", "Import","Help"]:
      #if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["View", "Edit", "Insert", "Add", "Import","Help"] or Global.work_area[Global.current_work_area_name]["action"] in ["List Users"]:
      #if Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["View", "Edit", "Insert", "Add", "Import"]:
        self.mb_middle.visible = False
        self.mb_search.visible = False
        self.mb_left.visible = False
      elif Global.work_area[Global.current_work_area_name]["action"].split(" ")[0] in ["List"]:
        self.mb_middle.visible = True
        self.mb_search.visible = True
        self.mb_left.visible = True

      self.select_all.indeterminate = False
      self.select_all.checked = False
      
      self.view_row.visible = True
      self.edit_row.visible = True if Global.login_site_user_role in ["Site Editor","Site Manager", "Site Leader"] or Global.login_system_user_role == "System Administrator" else False
      self.delete_row.visible = True if Global.login_site_user_role in ["Site Manager","Site Leader"] or Global.login_system_user_role == "System Administrator" else False
      if Global.table_name == "query":
        self.execute_sql.visible = True #if Global.site_user_role in ["Site Manager", "Site Leader"] or Global.system_user_role == "System Administrator" else False
      else:
        self.execute_sql.visible = False
      
      # for table dbdiary disable edit_row and delete_row button
      if Global.table_name == "dbdiary":
        self.view_row.visible = True
        self.edit_row.visible = False
        self.delete_row.visible = False
        self.execute_sql.visible = False
      # for table dbdiary disable edit_row and delete_row button
      if Global.table_name == "qresult":
        self.view_row.visible = True
        self.edit_row.visible = False
        self.delete_row.visible = False
        self.execute_sql.visible = False

      #
      #print("In create_new_work_area")
      table = Global.table_name
      if Global.table_name[0:2] == Global.prefix_special_finds_table:
        table = "fs tables"
      role = "System Administrator"
      if Global.login_system_user_role == "Site User":
        role = Global.login_site_user_role
      #print(role)
      #print(table)
      self.edit_row.visible = Global.role_access.get(role, {}).get(table, {}).get("Edit", None)
      self.delete_row.visible = Global.role_access.get(role, {}).get(table, {}).get("Delete", None)
      #print("set edit_row: " + str(self.edit_row.visible))
      #print("set delete_row: " + str(self.delete_row.visible))

      # safe edit_row and delete_row visibilty so that at click woekspace they can be set
      Global.work_area[Global.current_work_area_name]["visibility_view_row"] = self.view_row.visible
      Global.work_area[Global.current_work_area_name]["visibility_edit_row"] = self.edit_row.visible
      Global.work_area[Global.current_work_area_name]["visibility_delete_row"] = self.delete_row.visible
      Global.work_area[Global.current_work_area_name]["visibility_execute_sql"] = self.execute_sql.visible

      # Set selected buttons on Header for work area type
      #Global.action_form_type = Global.header_work_area_type.text
      #print(Global.action_form_type, Global.table_name)
      if Global.action_form_type in Global.action_forms_with_refresh:
        # make Refresh button visible if action_form_type has refresh function (i.e. in list Global.action_forms_with_refresh) 
        # do not do this for users table
        #self.refresh.visible = True if Global.table_name != "users" else False
        #print(action)
        # no refresh for View  and Edit and not for qresult
        self.refresh.visible = True if Global.table_name not in ["qresult"] and action.split(" ")[0].lower() not in ["view","edit"] else False
      else:
        #Global.header_refresh_button.visible = False
        self.refresh.visible = False

      if Global.action_form_type in Global.action_forms_with_print:
        # make print button visible if action_form_type has print function (i.e. in list Global.action_forms_with_print) 
        #Global.header_print_button.visible = True
        self.print.visible = True
      else:
        #Global.header_print_button.visible = False   
        self.print.visible = False

      # the following functionnis not yet fully implemented
      Function.set_allowed_actions()
      
      if Global.action_form_type in Global.action_forms_with_download:
        # Make download button visible for Global.action_form_type
        #Global.header_download_button.visible = True
        #print(Global.table_name, Global.login_site_user_role)
        self.download_csv.visible = True if Global.table_name not in ["online users","users"] and Global.login_site_user_role != "Site Viewer" else False
      else:
        #Global.header_download_button.visible = False
        self.download_csv.visible = False
      #print("download button "+str(self.download_csv.visible))
      #print(Global.action_form_type)
      #print(Global.action_forms_with_filter)
      if Global.action_form_type in Global.action_forms_with_filter and Global.work_area[work_area_name]["data_list"]:
        # Make filter button visible for Global.action_form_type if data_list is not empty
        #Global.header_filter_button.visible = True
        self.filter_cols.visible = True if Global.table_name not in ["online users","users","qresult","query"] else False
      else:
        #Global.header_filter_button.visible = False
        self.filter_cols.visible = False
      #print(self.filter_cols.visible)
      # reset action dropdown list
      #self.action_list.selected_value = None
      #Global.work_area[Global.current_work_area_name]["self"] = self
    else:
      n = Notification("This action has not yet been implemented.",timeout=Global.notification_timeout)
      n.show()
    pass # create_new_work_area
  
  def login_button_click(self, **event_args):
    """" This Function is called when the users logs in """
    """This method is called when the button is clicked"""
    #print("Login button clicked")
    user = anvil.users.login_with_form(allow_cancel=True,remember_by_default=False,show_signup_option=False)
    # check if user is logged in as newly registered account needs explicit enabling by administrator 

    if user is not None:
      # make welcome block of Main form invisible
      self.welcome_page.visible = False

      # notify server side of login
      Global.ip_address = anvil.server.call("user_authentication")

      # Update last_seen on page load
      self.refresh_online_count()

      # if user has system admin role, add system admin actions list and set it visible
      user = anvil.users.get_user()
      Global.login_system_user_role = user["systemrole"]
      Global.login_user_initials = user["initials"]
      self.user_role.text = Global.login_system_user_role
      #print(Global.system_user_role)
      
      # when user is logged in, enable Action menu, username field and logout button, and disable content panel (welcome message)
      # also set username  to user email address
      self.create_new_work_area("Help Introduction")
      #Global.username = user["email"]
      #Global.name = user["firstname"] + " " + user["lastname"]
      #message = Global.help_introduction.replace("<user>",Global.name)
      #rt = RichText(content=message,format="restricted_html")
      #Global.help_page_form.help_page_text.add_component(rt)
      
      self.username_dropdown.placeholder = Global.username
      self.username_dropdown.items = Global.username_dropdown_list

      # make menu bar variable visible
      self.menu_block.visible = True
      self.menu_top.visible = True
      self.title_panel.visible = True
      self.menu_middle.visible = True
      self.mm_left.visible = True
      self.mm_middle.visible = False      
      
      self.mm_right.visible = True
      if Global.login_system_user_role in ["System Administrator"]:
        self.menu_middle.visible = True
        self.mm_right.visible = True
        self.mm_left.visible = True
        self.mm_middle.visible = False
        self.admin_dropdown.visible = True
        self.menu_block.visible = True
        #self.menu_block.visible = False
        self.admin_dropdown.items = Global.sys_admin_action_dropdown
      
      # make menu bar variable visible
      ##self.menu_block.visible = True
      #self.menu_top.visible = True
      #self.title_panel.visible = True
      #self.menu_middle.visible = True
      #self.mm_left.visible = True
      
      Global.site_options = FunctionsB.set_select_site_dropdown_options()      
      self.select_site_dropdown.items = Global.site_options.keys()
      Global.select_site_dropdown = self.select_site_dropdown
      
      # create a introduction message and add it to the introduction_message of the introduction_message block and make it visible
      #Global.help_page.visible = True
      Global.site_id = "site_not_selected"
      
      Function.restore_workareas()

    pass # login_button_click

  def register_button_click(self, **event_args):
    """ This Function is called when a user wants to register himself"""
    """This method is called when the button is clicked"""
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user is not None:
      #print(str(user["email"]))
      #print(anvil.server.get_app_origin())
      #print(anvil.server.get_app_origin('published'))
      # send email notification to Project leader of the BAS system to finish the registration and enable the account
      msg = ("\nDear Project Leader for %s of the Anchurus-II Web Application,\n\n"
             "User %s has registered for an account to access the Anchurus-II system %s (URL: %s).\n"
             "Please check the new user account, complete the registration and then enable the account.\n\n"
             "Kind regards,\n\nThe Anchurus-II service"
             % (Global.organisation, str(user["email"]), Global.organisation, anvil.server.get_app_origin('published')))
      anvil.server.call("send_email","New user registration",msg,Global.admin_user)
      # notify user that the Project Leader will have to check and enable the user account
      msg = ("\nDear %s,\n\n"
             "Thank you for registering for access to %s system of the Anchurus-II Web Application (URL: %s)\n"
             "The project leader has been notified and will contact you when the registration has been validated.\n\n"
             "Kind regards,\n\nThe Anchurus-II service"
             % (str(user["email"]),Global.organisation,anvil.server.get_app_origin('published')))
      subject = ("Registration Anchurus-II system %s" % (anvil.server.get_app_origin('published')))
      anvil.server.call("send_email",subject,msg,str(user["email"]))
      msg = ("Thank you for registering. Your account registration request has been sent to the project leader for verification.\n"
             "You will be notified as soon as this has been completed. An email confirming your registration request has been sent to you.")
      alert(msg)
      # go back to login screen
      self.logout_click()
    else:
      alert("Registration cancelled")
      
    #if user is not None:
    #  # when user is logged in enable Action menu, username field and logout button, and disable content panel (welcome message)
    #  # also set username  to user email address
    #  Global.username = user["email"]
    #  self.username_dropdown.placeholder = Global.username
    #  #self.action_list.visible = True
    #  self.menu_top.visible = True
    #  self.welcome_page.visible = False
    pass # register_button_click

  def select_site_dropdown_change(self, **event_args):
    """ This Function is called when the users selects a site """
    """This method is called when an item is selected"""
    #print("select_site_dropdown selected")
    if self.select_site_dropdown.selected_value is not None and self.select_site_dropdown.selected_value != "No Sites available":
      # clear help_page_text 
      #Global.help_page.help_page_text.visible = True
      #Global.help_page.help_page_text.clear()
      #Global.help_page.visible = False
      
      Global.site_name = self.select_site_dropdown.selected_value
      Global.site_id = Global.site_options[self.select_site_dropdown.selected_value]
      Global.selected_site = ": " + Global.site_name
      #Global.title_label.text = Global.title + Global.status + Global.selected_site
      #Global.title_label.text = Global.title
      #Global.header_site_name.text = Global.site_name
      db_summary = anvil.server.call("db_get_summary",Global.site_id)
      self.site_summary.visible = True
      self.site_summary.items = db_summary

      #delete all work_areas and all work_area names/buttons and remove seq_no's
      temp_work_area_name_list = list(Global.work_area.keys())
      for work_area_name in temp_work_area_name_list:
        Function.delete_workspace(work_area_name)
        
      self.menu_bottom.visible = False
      self.site_summary.visible = False
      Global.action_seq_no = {}
      Global.work_area = {}
      # check user authorisation role for the selected site
      #print(Global.login_user_initials)
      Global.login_site_user_role = anvil.server.call("user_authorisation",Global.site_options[self.select_site_dropdown.selected_value],Global.login_user_initials)
      #print(Global.login_site_user_role)
      if Global.login_site_user_role != "unknown" or Global.login_system_user_role == "System Administrator":
        # user found with a role for the selected site
        #Global.help_page.visible = False
        self.site_summary.visible = True

        # Update role text if system_role is not System Administrator
        if Global.login_system_user_role == "Site User":
          self.user_role.text = Global.login_site_user_role

        if Global.login_site_user_role in ["Site Manager","Site Leader"]:
          # add site manager admin actions to admin dropdown
          options = Global.site_leader_action_dropdown + Global.site_admin_action_dropdown
          self.admin_dropdown.items = options
          self.admin_dropdown.visible = True
          
        if Global.login_system_user_role == "System Administrator":
          # add site manager / sie leader admin actions to admin dropdown
          options = Global.sys_admin_action_dropdown + Global.site_admin_action_dropdown
          self.admin_dropdown.items = options
          self.admin_dropdown.visible = True

        # Check permissions and build Query Dropdown list
        Global.query_action_dropdown = []
        role = "System Administrator"
        if Global.login_system_user_role == "Site User":
          role = Global.login_site_user_role
        #print(role)
        if Global.role_access.get(role, {}).get("query", {}).get("List", None):
          Global.query_action_dropdown.append(("List Query","List query"))
        if Global.role_access.get(role, {}).get("query", {}).get("Insert", None):
          Global.query_action_dropdown.append(("Insert Query","Insert query"))
        if Global.role_access.get(role, {}).get("query", {}).get("Import", None):
          Global.query_action_dropdown.append(("Import Query ","Import query"))
        self.query_dropdown.items = Global.query_action_dropdown
        
        Global.site_name = self.select_site_dropdown.selected_value
        Global.site_id = Global.site_options[self.select_site_dropdown.selected_value]
        Global.selected_site = ": " + Global.site_name
        #Global.title_label.text = Global.title + Global.status + Global.selected_site
        #Global.title_label.text = Global.title
        #Global.header_site_name.text = Global.site_name
        db_summary = anvil.server.call("db_get_summary",Global.site_id)
        self.site_summary.visible = True
        self.site_summary.items = db_summary

        if Global.login_site_user_role in ["Site Manager","Site Leader"] or Global.login_system_user_role == "System Administrator":
          self.list_dropdown.visible = True
          self.view_row.visible = True        
          self.edit_row.visible = True
          self.insert_dropdown.visible = True 
          self.query_dropdown.visible = True 
          self.delete_row.visible = True
          self.execute_sql.visible = False
          self.import_dropdown.visible = True
        elif Global.login_site_user_role in ["Site Editor"]:
          self.list_dropdown.visible = True
          self.view_row.visible = True        
          self.edit_row.visible = True
          self.insert_dropdown.visible = True 
          self.query_dropdown.visible = True 
          self.delete_row.visible = False
          self.execute_sql.visible = False
          self.import_dropdown.visible = False
        elif Global.login_site_user_role in ["Site Viewer"]:
          self.list_dropdown.visible = True
          self.view_row.visible = True
          self.edit_row.visible = False
          self.insert_dropdown.visible = False
          self.query_dropdown.visible = True 
          self.delete_row.visible = False
          self.execute_sql.visible = False
          self.import_dropdown.visible = False
        else:
          # unknown role
          msg = "Unkown User Role identified: " + str(Global.login_site_user_role)
          n = Notification(msg,timeout=Global.notification_timeout)
          n.show()
          # disable able all action buttons
          self.admin_dropdown.visible = False
          self.list_dropdown.visible = False
          self.view_row.visible = False
          self.edit_row.visible = False
          self.insert_dropdown.visible = False
          self.delete_row.visible = False
          self.execute_sql.visible = False
          self.import_dropdown.visible = False
        # now we can create a new site introduction work area.
        self.create_new_work_area("Site Introduction")
      else:
        msg = "Not found a role for you in site " + self.select_site_dropdown.selected_value + ". Please contact the Site Leader."
        Global.site_name = self.select_site_dropdown.selected_value
        Global.site_id = Global.site_options[self.select_site_dropdown.selected_value]
        Global.selected_site = ": " + Global.site_name
        #Global.site_name = ""
        #Global.site_id = ""
        #Global.selected_site = ""
        #self.select_site_dropdown.selected_value = None
        n = Notification(msg,timeout=Global.notification_timeout)
        n.show()
      #
      self.menu_middle.visible = True
      self.mm_left.visible = True
      self.mm_middle.visible = True
      self.mm_right.visible = True     
      Function.restore_workareas()
    else:
      self.select_site_dropdown.selected_value = None
    pass # select_site_dropdown_change

  # Funtions for the menu options (Menu_middle) after the user selected a site
  def admin_dropdown_change(self, **event_args):
    """ This Function is called when the users has selected an action form the Admin dropdown menu """
    """This method is called when an item from the dropdown menu is selected"""
    # Action has been selected, but only take action if action in not a separator
    # save a link to the Main form in a Global variable 
    #Global.main_form = get_open_form()
    #Global.help_page.visible = False

    Global.action = self.admin_dropdown.selected_value
    #print(Global.action)
    if Global.action not in Global.action_list_not_implemented:
      #print(Global.action)
      #print(Global.action_list_not_implemented)
      self.create_new_work_area(Global.action)
    else:
      if Global.action != Global.separator:
        alert("Action not yet implemented.")
        
    # clear selected_value
    self.admin_dropdown.selected_value = None
    pass # admin_dropdown_change

  def insert_dropdown_change(self, **event_args):
    """ This Function is called when the users selects an option form the Insert dropdown"""
    """This method is called when an item is selected"""
    #Global.main_form = get_open_form()
    # make action to be "Insert ..." 
    Global.action = "Insert " + str(self.insert_dropdown.selected_value).capitalize()
    #print("Insert action - ",Global.action)
    if Global.action not in Global.action_list_not_implemented:
      # Action has been selected, create button in work area list, and make this work area in focus (highlight button)
      # for any action that has a Form defined create a new work_area
      if Global.site_id is None and Global.action not in (Global.sys_admin_action_dropdown) and Global.action not in (Global.site_admin_action_dropdown) :
        # if site is not yet selected alert user
        alert(
          content="Site has not been selected. Please select a site.",
          title="Site selection warning",
          large=True,
          buttons=[("Ok", True)],
        )
      else:
        self.create_new_work_area(Global.action)
    else:
      if Global.action != Global.separator:
        print(Global.action)
        alert("Action not yet implemented.")

    # clear selected_value
    self.insert_dropdown.selected_value = None
    pass # insert_dropdown_change

  def list_dropdown_change(self, **event_args):
    """ This Function is called when the users selects an option form the List dropdown"""
    """This method is called when an item is selected"""
    # clear selected_value
    #Global.main_form = get_open_form()
    # make action to be "List ..."
    Global.action = "List " + str(self.list_dropdown.selected_value).capitalize()
    
    if Global.action not in Global.action_list_not_implemented:
      # Action has been selected, create button in work area list, and make this work area in focus (highlight button)
      # for any action that has a Form defined create a new work_area
      if Global.site_id is None and Global.action not in (Global.sys_admin_action_dropdown) and Global.action not in (Global.site_admin_action_dropdown) :
        # if site is not yet selected alert user
        alert(
          content="Site has not been selected. Please select a site.",
          title="Site selection warning",
          large=True,
          buttons=[("Ok", True)],
        )
      else:
        self.create_new_work_area(Global.action)
    else:
      if Global.action != Global.separator:
        alert("Action not yet implemented.")
    
    self.list_dropdown.selected_value = None
    pass # list_dropdown_change

  def import_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    """ This Function is called when the users selects an option form the Import dropdown"""
    #print("Import dropdown")
    #Global.main_form = get_open_form()
    # set action
    Global.action = "Import " + str(self.import_dropdown.selected_value).capitalize()
    #print("Import action - ",Global.action)
    if Global.action not in Global.action_list_not_implemented:
      # Action has been selected, create button in work area list, and make this work area in focus (highlight button)
      # for any action that has a Form defined create a new work_area
      if Global.site_id is None and Global.action not in (Global.sys_admin_action_dropdown) and Global.action not in (Global.site_admin_action_dropdown)  :
        # if site is not yet selected alert user
        alert(
          content="Site has not been selected. Please select a site.",
          title="Site selection warning",
          large=True,
          buttons=[("Ok", True)],
        )
      else:
        #print("Import action: ",Global.action)
        self.create_new_work_area(Global.action)
    else:
      if Global.action != Global.separator:
        alert("Action not yet implemented.")

    # clear selected_value

    self.import_dropdown.selected_value = None
    pass # import_dropdown_change

  def help_dropdown_change(self, **event_args):
    """ This Function is called when the users selects an option form the Help dropdown"""
    """This method is called when an item is selected"""
    #Global.main_form = get_open_form()
    Global.action = self.help_dropdown.selected_value
    if Global.action == "Anchurus Website":
      new_tab = anvil.js.window.open("https://anchurus.co.uk", '_blank')
      if new_tab is None:
        print("The window was blocked by a popup blocker!")
      else:
        print("Window opened successfully.")
    self.help_dropdown.selected_value = None
    pass # help_dropdown_change

  def site_summary_change(self, **event_args):
    """ This Function is called when the users selects an option form the Site Summary dropdown"""
    """This method is called when an item is selected"""
    # here we do not do anything except set the selected value of the dropdown to None
    self.site_summary.selected_value = None
    pass # site_summary_change

  # Functions on the header for the work area
  #def selection_change(self, **event_args):
  #  # This function is not used here. It is the one in TableList
  #  print("selection_change in Main")
  #  rows = [row for row in Global.work_area[Global.current_work_area_name]["self"].repeating_panel_1.get_components()]
  #  any_checked = any(row.btn_select.checked for row in rows)
  #  all_checked = all(row.btn_select.checked for row in rows)
  #  #
  #  #self.select_all.checked = any_checked
  #  #self.select_all.indeterminate = not all_checked and any_checked
  #  ###Global.work_area[Global.current_work_area_name]["self"].select_all.checked = any_checked
  #  ###Global.work_area[Global.current_work_area_name]["self"].select_all.indeterminate = not all_checked and any_checked
  #  Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = any_checked
  #  #
  #  pass # selection_change
  
  def select_all_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    #print("select_all_change from Main")
    checked = self.select_all.checked
    indetermined = self.select_all.indeterminate
    #print("Select_all button clicked: ",Global.current_work_area_name, " checked: ",checked, " indeterminate: ",indetermined)
    #
    if self.select_all.indeterminate:
      # if indeterminate is True, force check to False
      checked = False
    #for row in self.repeating_panel_1.get_components(): 
    for row in Global.work_area[Global.current_work_area_name]["self"].repeating_panel_1.get_components():
      prev_status_btn_select = row.btn_select.checked
      row.btn_select.checked = checked
      #
      if checked:
        Global.work_area[Global.current_work_area_name]["selected_rows"].append(row.item)
        row.background = Global.selected_highlight_colour
      else:
        if prev_status_btn_select:
          Global.work_area[Global.current_work_area_name]["selected_rows"].remove(row.item)
          row.background = ""
    #
    if self.select_all.indeterminate:
      #print("if indeterminate was True, set indeterminate to False ")
      self.select_all.indeterminate = False
      self.select_all.checked = False
      ###Global.work_area[Global.current_work_area_name]["self"].select_all.indeterminate = False
    #
    if len(Global.work_area[Global.current_work_area_name]["selected_rows"]) == 0:
      #print("0 selected rows, clear menu")
      Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = False
      ###Global.work_area[Global.current_work_area_name]["self"].select_all.checked = False
      self.select_all.checked = False
    else:
      Global.work_area[Global.current_work_area_name]["menu_select_options"].visible = True

    ###Global.work_area[Global.current_work_area_name]["self"].select_all.checked = checked
    self.select_all.checked = checked
    pass # select_all_change
    
  def view_row_click(self, **event_args):
    """This method is called when the button is clicked"""
    #
    for row in Global.work_area[Global.current_work_area_name]["selected_rows"]:
      Global.table_items = row
      #print("View button for row: ",row)
      Global.action = "View " + Global.table_name.capitalize()
      #print("In view_row: "+Global.action)
      #if Global.action == "View Qresult":
        #print("View_row click. Check Global.query_id: "+Global.query_id)
      if Global.main_form:  # Important to check if the form exists
        # Create new work_area 
        Global.main_form.create_new_work_area(Global.action)
      else:
        print("Main form not found!")
    pass # view_row_click

  def edit_row_click(self, **event_args):
    """This method is called when the button is clicked"""
    #
    for row in Global.work_area[Global.current_work_area_name]["selected_rows"]:
      Global.table_items = row
      Global.action = "Edit " + Global.table_name.capitalize()
      if Global.main_form:  # Important to check if the form exists
        # Create new work_area  
        Global.main_form.create_new_work_area(Global.action)
      else:
        print("Main form not found!")
    pass # edit_row_click

  def delete_row_click(self, **event_args):
    """This method is called when the button is clicked"""
    message = "\nYou have seleted to delete the follow(ing) row(s) from table " + Global.table_name.capitalize() + "\n\n"
    rows_to_delete = []
    # loop through selected rows
    for row in Global.work_area[Global.current_work_area_name]["selected_rows"]:
      Global.table_items = row
      delete_row_keys = {}
      # select PRI Keys for rows to delete
      for item in Global.work_area[Global.current_work_area_name]["table_info"]:
        if item['COLUMN_KEY'] == "PRI":
          col_name = item["COLUMN_NAME"]
          Global.action = "Delete " + Global.table_name.capitalize()
          message = message + col_name + ": " + row[col_name] + ", "
          delete_row_keys[col_name] = row[col_name]
      # add delete_row_keys to list of rows_to_delete
      rows_to_delete.append(delete_row_keys)
      message = message.rstrip(", ")
      message = message + "\n"
      
    # ask confirmation to delete selected rows
    message = message + "\n\nDo you wish to continue?"
    if confirm(message):
      # confirmation to delete the slected rows
      # call server function to do the actual deletion
      msg = anvil.server.call('delete_row',Global.table_name,rows_to_delete)
      # update Site Summary
      db_summary = anvil.server.call("db_get_summary",Global.site_id)
      Global.main_form.site_summary.visible = True
      Global.main_form.site_summary.items = db_summary
      alert(msg)
    pass # delete_row_click

  def first_page_click(self, **event_args):
    """This method is called when the button is clicked"""
    FunctionsB.clear_selection(Global.work_area[Global.current_work_area_name]["self"])
    Global.work_area[Global.current_work_area_name]["self"].table.set_page(0)
    FunctionsB.update_status_label(Global.work_area[Global.current_work_area_name]["self"])
    pass # first_page_click
 
  def prev_page_click(self, **event_args):
    """This method is called when the button is clicked"""
    FunctionsB.clear_selection(Global.work_area[Global.current_work_area_name]["self"])
    Global.work_area[Global.current_work_area_name]["self"].table.set_page(Global.work_area[Global.current_work_area_name]["self"].table.get_page() - 1)
    FunctionsB.update_status_label(Global.work_area[Global.current_work_area_name]["self"])
    pass # prev_page_click

  def next_page_click(self, **event_args):
    """This method is called when the button is clicked"""
    #print("next_page_click")
    FunctionsB.clear_selection(Global.work_area[Global.current_work_area_name]["self"])
    Global.work_area[Global.current_work_area_name]["self"].table.set_page(Global.work_area[Global.current_work_area_name]["self"].table.get_page() + 1)
    FunctionsB.update_status_label(Global.work_area[Global.current_work_area_name]["self"])
    pass # next_page_click

  def last_page_click(self, **event_args):
    """This method is called when the button is clicked"""
    #print("last_page_click")
    FunctionsB.clear_selection(Global.work_area[Global.current_work_area_name]["self"])
    rows_per_page = int(Global.work_area[Global.current_work_area_name]["self"].table.rows_per_page)
    total_rows = len(Global.work_area[Global.current_work_area_name]["self"].repeating_panel_1.items)
    Global.work_area[Global.current_work_area_name]["self"].table.set_page(total_rows // rows_per_page)
    FunctionsB.update_status_label(Global.work_area[Global.current_work_area_name]["self"])
    pass # last_page_click

  def filter_cols_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Here we allow the user to filter columns to be viewed
    # extract table columns names and sort them in the order as set in the DB table
    col_order = Global.work_area[Global.current_work_area_name]["col_order"]
    # remove DBAcontrol column name as it is not in the table
    col_order.pop("DBAcontrol")
    col_order_sorted = sorted(col_order, key=lambda x: col_order.get(x,999))
    # 1. Define the options you want to display
    option_id = 0
    options_data = []
    for column_name in col_order_sorted:
      option_id = option_id + 1
      options_data.append({'text': column_name, 'id': option_id})

    # 2. Create an instance of your Dialog Form
    dialog = FilterList(options_list=options_data)

    # 3. Use alert() to show the form as a modal popup
    # The alert() function will return the 'value' passed when 'x-close-alert' is raised
    selected_list = alert(
      content=dialog, 
      title="Filter Columns",
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
      #cleaned_list.sort()
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
      FunctionsB.table_list_refresh(Global.work_area[Global.current_work_area_name]["self"])
    pass # filter_cols_click

  def download_csv_click(self, **event_args):
    """This method is called when the button is clicked"""
    # call server-side function create_csv to create a csv file and download this to user Download folder
    file_name = Global.current_work_area_name + ".csv"
    
    # create ordinal_position list of columns 
    col_order = {}
    position = 0
    for column in Global.work_area[Global.current_work_area_name]["table"].columns:
      #print(column["data_key"])
      if Global.table_name != "users":
        position = next((item['ORDINAL_POSITION'] for item in Global.work_area[Global.current_work_area_name]["table_info"] if item['COLUMN_NAME'] == column["data_key"]),0)
      else:
        position = position + 1
      col_order[column["data_key"]] = position
      
    # make sure to send the col_order as a list []
    csv_file = anvil.server.call('create_csv',Global.work_area[Global.current_work_area_name]["data_list"],[col_order],file_name)
    anvil.media.download(csv_file)
    pass # download_csv_click

  def print_click(self, **event_args):
    """This method is called when the button is clicked"""
    form = str(type(Global.work_area[Global.current_work_area_name]["form"])).split(".")[2][:-2]
    #print("From new print_click, form to use and send to server function: ",form)
    # table names are all lowercase and singular, so create table name from action
    tmp_name = Global.work_area[Global.current_work_area_name]["action"].split(" ",1)[1]
    table_name = tmp_name.lower()

    # call the print_form at the server-side
    pdf_form = anvil.server.call('print_form',form,Global.site_id,table_name.strip(),
                                 Global.work_area[Global.current_work_area_name]["action"],
                                 Global.work_area[Global.current_work_area_name]["data_list"],
                                 Global.work_area[Global.current_work_area_name]["page_info"]
                                )
    anvil.media.download(pdf_form)
    pass # print_click

  def refresh_click(self, **event_args):
    """This method is called when the button is clicked"""
    # call refresh function for the work_area
    FunctionsB.refresh_click(Global.work_area[Global.current_work_area_name]["self"])
    pass # refresh_click

  def del_work_area_click(self, **event_args):
    """This method is called when the button is clicked"""
    # call delete work_area function
    Function.delete_workspace(Global.current_work_area_name)
    pass # del_work_area_click

  def logout_click(self, **event_args):
    """This method is called when the button is clicked"""
    # logout user, hide action menu, username and logout button; also delete all workspaces
    anvil.server.call("user_logout_notification",Global.ip_address,Global.username)
    anvil.users.logout()

    # make help_page invisible
    #Global.help_page.visible = False
    #Global.help_page.help_page_text.clear()
    
    # Welcome_page will show the login page
    self.welcome_page.visible = True

    # make menu block and admin menu invisible
    self.menu_block.visible = True
    self.title_panel.visible = True
    self.menu_top.visible = False
    self.menu_middle.visible = False
    self.mm_left.visible = True
    self.mm_middle.visible = False
    self.mm_right.visible = False
    self.admin_dropdown.visible = False
    self.site_summary.visible = False
    self.menu_bottom.visible = False

    self.admin_dropdown.items = []
    self.username_dropdown.placeholder = Global.username
    self.username_dropdown.items = []
    
    Global.login_system_user_role = ""
    Global.login_system_user_role = ""
    Global.login_site_user_role = ""
    Global.login_user_initials = ""
    Global.login_user_firstname = ""
    Global.login_user_lastname = ""
    Global.login_user_status = ""
    
    self.user_role.text = ""

    # To be done: save work areas in table for user for loading when login

    #delete all work_areas and all work_area names/buttons
    temp_work_area_name_list = list(Global.work_area.keys())
    for work_area_name in temp_work_area_name_list:
      Function.delete_workspace(work_area_name)

    # clear selected site
    self.select_site_dropdown.selected_value = None

    # clear work_area list and action_seq_no
    Global.work_area = {}
    Global.action_seq_no = {}
    pass # logout_click

  def username_dropdown_change(self, **event_args):
    """ This Function is called when the users has selected the logout option of the username dropdown """
    """This method is called when an item is selected"""
    # But we just check in case it is not ;)
    #print(self.username_dropdown.selected_value)
    if self.username_dropdown.selected_value == "Change password":
      user = anvil.users.get_user()
      success = anvil.users.change_password_with_form(require_old_password=True)
      if success:
        msg = ("\nDear %s %s,\n\n"
               "Just to confirm you that your password for the Anchurus-II service for %s has been updated.\n\n"
               "The Anchurus-II service"
               % (str(user["firstname"]),str(user["lastname"]), Global.organisation, ))
        n = Notification(msg,timeout=Global.notification_timeout)
        n.show()
        anvil.server.call("send_email","Password reset",msg,user["email"])

    elif self.username_dropdown.selected_value == "Save all work areas":
      name = "Saved_areas " + Global.site_id
      work_area_dict = {}
      temp_work_area_name_list = list(Global.work_area.keys())
      # loop through all work_area and build a nested dictionary with further information (do not need to usee all of work_area dict)
      # may want to add more information (e.g. add column filter information of work area in order to restore it with the filter)
      for work_area_name in temp_work_area_name_list:
        if work_area_name in ["Introduction","Help Introduction","Site introduction"]:
          continue
        work_area_dict[work_area_name] = {}
        work_area_dict[work_area_name]["action"] = Global.work_area[work_area_name]["action"]
        work_area_dict[work_area_name]["site_id"] = Global.work_area[work_area_name]["site_id"]
        work_area_dict[work_area_name]["site_name"] = Global.work_area[work_area_name]["site_name"]
        work_area_dict[work_area_name]["table_info"] = Global.work_area[work_area_name]["table_info"]
        work_area_dict[work_area_name]["data_list"] = Global.work_area[work_area_name]["data_list"]
        #print("In Save workarea environment. table_info is " + str(Global.work_area[work_area_name]["table_info"]))
        work_area_dict[work_area_name]["form_type"] = Global.work_area[work_area_name]["form_type"]
        if Global.work_area[work_area_name].get("query_info"):
          #print("In Save workarea environment. Query_info is " + str(Global.work_area[work_area_name]["query_info"]))
          work_area_dict[work_area_name]["query_info"] = Global.work_area[work_area_name]["query_info"]
        if Global.work_area[work_area_name].get("column_order"):
          work_area_dict[work_area_name]["column_order"] =  Global.work_area[work_area_name]["column_order"]
        if Global.work_area[work_area_name].get("tmp_table_info"):
          work_area_dict[work_area_name]["tmp_table_info"] =  Global.work_area[work_area_name]["tmp_table_info"] 
                
        #print(work_area_name)
        #print(Global.work_area[work_area_name]["form_type"])
        if Global.work_area[work_area_name]["form_type"] == "RowForm":
          # only for RowForm we need to keep the data_list (is one record); for a TableList form we will do a refresh 
          #print(len(Global.work_area[work_area_name]["data_list"]))
          work_area_dict[work_area_name]["data_list"] = Global.work_area[work_area_name]["data_list"]
        
      #print("Calling save_workareas")
      msg = anvil.server.call("save_workareas",name,work_area_dict,Global.site_id)
      n = Notification(msg,timeout=Global.notification_timeout)
      n.show()
      #alert(msg,title="Saving work area notification")
    elif self.username_dropdown.selected_value == "Clear saved work areas":
      name = "Saved_areas " + Global.site_id
      msg = anvil.server.call("clear_saved_workareas",name)
      n = Notification(msg,timeout=Global.notification_timeout)
      n.show()
      #alert(msg,title="Clearing work area notification")
    elif self.username_dropdown.selected_value == "Close all work areas":
      # Close all work_areas and all work_area names/buttons
      temp_work_area_name_list = list(Global.work_area.keys())
      for work_area_name in temp_work_area_name_list:
        Function.delete_workspace(work_area_name)
      Global.action_seq_no = {}
      Global.work_area = {}
    elif self.username_dropdown.selected_value == "Logout":
      self.logout_click()

    #clear selected option
    self.username_dropdown.selected_value = None
    pass # username_dropdown_change

  @handle("query_dropdown", "change")
  def query_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    # ceate new work area for query action
    Global.action = self.query_dropdown.selected_value
    self.create_new_work_area(Global.action)
    self.query_dropdown.selected_value = None
    pass # query_dropdown_change

  @handle("execute_sql", "click")
  def execute_sql_click(self, **event_args):
    """This method is called when the button is clicked"""
    for row in Global.work_area[Global.current_work_area_name]["selected_rows"]:
      # loop through all selected rows
      Global.table_items = row
      Global.query_info = row

      Global.query_id = row["QueryId"]
      command = row["SQL_command"]
      #print(command)
      if command != "":
        msg, data_list, column_order, Global.tmp_table_info = anvil.server.call("execute_sql_command",command)
        #print("after server call to exececute_sql_command. tmp_table_info is "+str(Global.tmp_table_info))
      else:
        msg = "FAIL: SQL command field is empty."
      
      # Check msg for succes or FAIL
      if msg[0: 4] == "FAIL":
        alert(msg)
      else:
        # SQL command completed successfully and returned a data_list. Create a new TableList workspace for the results
        Global.column_order = column_order
        #print("after execute_sql_command. column_order is "+str(column_order))
        Global.table_items = data_list
        Global.table_name = "qresult"
        Global.action = "List " + Global.table_name.capitalize()
        if Global.main_form:  # Important to check if the form exists
          # Create new work_area 
          Global.main_form.create_new_work_area(Global.action)
        else:
          print("Main form not found!")
    pass # execute_sql_click

  @handle("search_btn", "click")
  def search_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass  # Write Code Here

  def refresh_online_count(self):
    """Calls server silently and updates the text label."""
    # Use call_s (silent) to avoid showing the loading spinner
    count = anvil.server.call_s("update_user_last_seen")
    #print("Online users: "+str(count))
    # Update your label text
    self.online_users.text = f"🟢 Online Users: {count}"
    pass
    
  @handle("timer_activity", "tick")
  def timer_activity_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    # interval should be set to 120 seconds in time properties
    
    # Get the JavaScript timestamp (in milliseconds)
    last_js_activity = window.lastUserActivity
   
    # If a user is logged in and user interacted since our last server update, ping the server
    if Global.login_user_initials != "" and last_js_activity > self.last_server_update:
      self.refresh_online_count()
      self.last_server_update = window.Date.now()
    pass  # 

