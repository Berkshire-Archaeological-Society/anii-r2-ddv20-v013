import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .. import Module1
#
#    Module1.say_hello()
#
# Global Variables
#
main_form = ""
separator = "------------------"
sys_admin_action_list = ["List Users","Edit User","Insert User","Import Users",separator,"List Site","Edit Site","Add Site"]
site_leader_action_list = ["List Users",separator,"List Site","Edit Site","Add Site"]
site_admin_action_list = [separator,"List UserRole","Edit UserRole","Add UserRole","Import UserRoles"]
admin_action_list_not_implemented = [separator]
#user_action_list = ["Select Site",separator,
#                    "List Contexts","Add Context","Bulk Upload Contexts",separator,
#                    "List Finds", "Add Find","Bulk Upload Finds",separator,
#                    "List Anomalies","Add Anomaly",separator,
#                    "List Interpretations","Add Interpretation"
#                   ]
# action_list_not_implemented should always contain the separator
#action_list_not_implemented = [separator,"Bulk Upload Finds","Draw","List Areas","Add Area","Add Anomaly"]
action_list_not_implemented = [separator]
# the list_action_list is a list of the tables in DB (not yet sites)
list_action_dropdown = []
insert_action_dropdown = []
file_action_dropdown = ["Import",separator,"Save"]
view_action_dropdown = []
help_action_dropdown = ["Anchurus Website"]
query_action_dropdown = [("List Query","List query"),("Insert Query","Insert query"),("Import Query ","Import query")]
sys_admin_action_dropdown = [("List System Users","List Users"),("Insert System User","Insert User"),("Import System Users","Import Users"),("List Online Users","List Online Users"),separator,("List DBDiary","List dbdiary"),separator,("List Sites","List Site"),("Insert Site","Insert Site")]
site_leader_action_dropdown = [("List System Users","List Users"),separator,("List DBDiary","List dbdiary"),separator,("List Sites","List Site")]
site_admin_action_dropdown = [(separator,separator),("List Site Users","List siteuserrole"),("Insert Site User","Insert siteuserrole"),("Import Site Users","Import siteuserrole")]
#
import_action_dropdown = ["context","find"]
#
action_forms_with_refresh = ["TableList","RowForm","ListUsers","ListSites","ListContexts","ListFinds","ListAreas","BulkUpload","Add Area","List Areas"]
action_forms_with_print = []
action_forms_with_download = ["ListContexts","ListFinds","TableList"]
action_forms_with_filter = ["ListContexts","ListFinds","TableList"]
#
action_seq_no = {}
csv_file = None
current_work_area = {}
current_work_area_name = ""
current_work_area_type = ""
restore_workarea_name = ""
# variables for work area header
header = {}
header_work_area_name = {}
header_refresh_button = {}
header_print_button = {}
header_download_button = {}
header_filter_button = {}
header_work_area_type= {}
header_site_name = {}
header_site_summary_information = {}
# variables for Global Header dropdown lists
gh_file_list = {}
gh_view_list = {}
gh_help_list = {}
gh_list_list = {}
gh_insert_list = {}
gh_admin_list = {}
#

work_area = {}
# variable for work area header menu options 
wa_header_menu_bottom = {}
wa_header_mb_left = {}
wa_header_mb_middle = {}
wa_header_mb_search = {}
wa_header_mb_right = {}
#
selected_row = []
selected_highlight_colour = "#66FFFF"
#
menu_select_options = ""
Quill_toolbarOptions = [
['bold', 'italic', 'underline', 'strike'],        # toggled buttons
['link'],
[{ 'header': 1 }, { 'header': 2 }],               # custom button values
[{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
[{ 'script': 'sub'}, { 'script': 'super' }],      # superscript/subscript
[{ 'indent': '-1'}, { 'indent': '+1' }],          # outdent/indent
[{ 'direction': 'rtl' }],                         # text direction
[{ 'size': ['small', 'normal', 'large', 'huge'] }],  # custom dropdown
[{ 'header': [1, 2, 3, 4, 5, 6] }],
[{ 'color': [] }, { 'background': [] }],          # dropdown with defaults from theme
[{ 'font': [] }],
[{ 'align': [] }],
['clean']                                         # remove formatting button
]
#
# for every table (both Anvil tables and DB tables) we need an entry in this multi-level dictionary. There is one entry for all find specialists tables (fs tables), so for these there is no need for a entry per fs table.
# 
role_access = {
'Site Viewer': {
  "anomaly":         {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  "context":         {'List': True,  'View': True,  'Edit': False, 'Insert': False,' Import': False, 'Export': False, 'Delete': False},
  "find":            {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'findgroup':        {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'fs tables':       {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'ircollection':    {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},  
  'ircollectfind':   {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},  
  'box':             {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'trackbox':        {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'phase':           {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'groups':           {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'sets':             {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'interpretation':        {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'stratigraphicanalysis': {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'query':           {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'site':            {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'siteuser':        {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'siteuserrole':    {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'dbdiary':         {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'users':           {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False}
  },
'Site Editor': {
  'anomaly':         {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'context':         {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'find':            {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'findgroup':        {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'fs tables':       {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'ircollection':    {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'ircollectfind':   {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'box':             {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'trackbox':        {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'phase':           {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'groups':           {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'sets':             {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'interpretation':        {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'stratigraphicanalysis': {'List': True,  'View': True,  'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'query':           {'List': True,  'View': True,  'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'site':            {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'siteuser':        {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'siteuserrole':    {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'dbdiary':         {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'users':           {'List': False, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False}
  } ,
'Site Leader': {
  'anomaly':         {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'context':         {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'find':            {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'findgroup':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'fs tables':       {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'ircollection':    {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'ircollectfind':   {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'box':             {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'trackbox':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'phase':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'groups':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'sets':             {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'interpretation':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'stratigraphicanalysis': {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'query':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': False},
  'site':            {'List': True, 'View': True, 'Edit': True,  'Insert': False, 'Import': False, 'Export': True,  'Delete': False},
  'siteuser':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'siteuserrole':    {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'dbdiary':         {'List': True, 'View': True, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'users':           {'List': True, 'View': False, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False}
  },
'System Administrator': {
  'anomaly':         {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'context':         {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'find':            {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'findgroup':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'fs tables':       {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'ircollection':    {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'ircollectfind':   {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'box':             {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'trackbox':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'phase':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'groups':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'sets':             {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'interpretation':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'stratigraphicanalysis': {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'query':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'site':            {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'siteuser':        {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'siteuserrole':    {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True},
  'dbdiary':         {'List': True, 'View': True, 'Edit': False, 'Insert': False, 'Import': False, 'Export': False, 'Delete': False},
  'users':           {'List': True, 'View': True, 'Edit': True,  'Insert': True,  'Import': True,  'Export': True,  'Delete': True}  
  }
}
button_normal_background_clour = "#DCE5DD"
button_highlight_background_clour = "#CBEAD6"
#
action = ""
action_form_type = ""
admin_action = ""
admin_domain = ""
admin_user = ""
admin_user_initials = ""
area_items = {}
area_id = None
area_options = {}
db_name = ""
dummy_btn1 = {}
dummy_btn2 = {}
# the following global variables contains details of columns
column_order = {}
# the columns of the users table to be ignored in TableList
ignore_users_columns = ["remembered_logins","n_password_failures","password_hash","confirmed_email","email_confirmation_key","signed_up","remembered_logins","mfa"]
columns_not_editable = ["email","initials","last_login","password_hash", "n_password_failures","confirmed_email","signed_up","email_confirmation_key","remembered_logins","mfa","last_seen"]
# predefined width of known columns
column_width = {"initials": 60,
                "firstname": 150,
                "lastname":150,
                "systemrole": 140,
                "last_seen": 210,
                "last_login": 210,
                "YearStart": 75,
                "YearEnd": 70,
                "Count": 50,
                "Width": 50,
                "Depth": 50,
                "Length": 60
               }
# dropdown lilst for listed columns (for data input)
column_with_dropdown = {
  "Enabled" : {
    "options"     : ["True", "False"], 
    "placeholder" : "Please select 'True' or 'False'", 
    "error"       : "You must make a selection"
  }, 
  "ContextType" : {
    "options"     : ["Deposit","Fill","Cut","Structure","Feature"], 
    "placeholder" : "Please select a type", 
    "error"       : "You must make a selection"
  },
  "Role" : {
    "options"     : ["Site Leader","Site Editor","Site Viewer"], 
    "placeholder" : "Please select a role", 
    "error"       : "You must make a selection"
  },
  "SurveyMethod" : {
    "options"     : ["BNG", "Aligned to BNG north", "Not aligned to BNG north"],
    "placeholder" : "Please select a survey method", 
    "error"       : "You must make a selection"    
  },
  "FindType" : {
    "options"     : ["Bulk", "SmallFind", "Sample", "Group", "FindGroup"],
    "placeholder" : "Please select a type", 
    "error"       : "You must make a selection"    
  },
  "systemrole":{
    "options"     : ["System Administrator", "Site User"],
    "placeholder" : "Please select a type", 
    "error"       : "You must make a selection"
  }
}
#
context_id = None
context_items = {}
context_options = {}
context_types = ["Deposit","Cut","Structure"]
copyright = ""
DBAcontrol = ""
field_description_changed = False
file = []
find_id = None
file_list = []
find_items = {}
find_options = {}
find_types = {"Bulk Find","Small Find","Sample","FindGroup"}
google_link = ""
context_help_information = """
Deposit description:
1. Colour 2. Consistency 3. Texture 4. lnclusions (<50%) 5. Thickness and extent, 5. Other comments. 7. Method and conditions
Cut description:
1. Shape in plan (sketch overleaf) 2. Corners 3. Dimensions/depth 4. Break of slope -top 5. Sides, 6. Break of slope -
base 7. Base 8. Orientation 9. Shape of profile (sketch overleaf) 10. Fill Nos 11. Other comments
Masonry description:
1. Materials 2. Size of materials (brick; BLT in mm) 3. Finish of stones,4. Coursing/bond 5. Form 6. Direction of
face(s) 7. Bonding material (brick height of 4 courses and 4 bed joints in mm 8 . Dimensions of masonry as found 9. Other comments 
"""
image_type = ""
ip_address = ""
print_action = False
selected_material_types = {}
material_types = ["CBM Tile","CBM Brick","CBM Drain Pipe","CBM Mortar",
                  "Stone","Roofing Slate","Flint","Worked Flint","Pottery",
                  "Clay Pipe","Metalwork","Nails","Iron Slag","Glass","Animal Bone",
                  "Oyster Shells","Wood","Charcoal"]
login_options = {"Sign in", "Sign out"}
#
notification_timeout = 10
organisation = ""
query_view = False
query_id = ""
query_info = []
view_queries = ["siteuserrole"]
#
# The following variable rows_per_page has to be set to 0, to make sure the print function prints the whole table
# During startup of the client (i.e. browser URL click of website) this value can be overwritten by a value for this
# defined in the server side configuration file
# Note that the 'page' is this context is a webpage and not a physical printing page
rows_per_page = 0 
#
selected_site = ""
sign_in_out_button_text = "Sign in"
site_id = None
site_name = ""
site_options = {}
site_items = {}
select_site_dropdown = {}
header_site_summary_information = {}
prefix_special_finds_table = ""
system_name = ""
SurveyMethod_options = {"BNG","Aligned to BNG north","Not aligned to BNG north"}
system = "Anchurus-II Web Application"
status = ""
#
table_name = ""
tmp_table_info = []
table_items = {}

#
title = system + "\n\n" + organisation
sign_in_out_button_text = "Sign in"
username = ""
password = ""
name = ""
user_firstname = ""
user_lastname = ""
user_initials = ""
system_user_role = ""
site_user_role = ""
user_status = ""
login_system_user_role = ""
login_site_user_role = ""
login_user_initials = ""
login_user_firstname = ""
login_user_lastname = ""
login_user_status = ""
site_user_role_options = {"Site Viewer","Site Editor","Site Leader","Administrator"}
system_user_role_options = {"Site User","System Administrator"}
user_status_options = {"True", "False"}
user_items = {}
username_dropdown_list = ["Close all work areas","Save all work areas","Clear saved work areas","Change password","Logout"]
config_version = ""

#
about_us_text = """
<h3>Welcome to the Anchurus-II R2 Web Application</h3>

<p>
This system allows for the digital recording of archaeological excavations.
The software has been developed by Archaeology IT Solutions, an independent 'not-for-profit' or 'nonprofit' organisation developing software solutions for the archaeological community.
It is developed using the <a href="https://anvil.works/" target="_blank>Anvil Framework</a> and is using the open source Anvil App Server which allows to run the application on your
own dedicated server. It uses its own MariaDB database to store the excavation details.  
This software is released under Creative Commons license: 
<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target=_blank>Attributions-NonCommercial-ShareAlike 4.0 International (CC BY-NC-AS 4.0) license</a>.
</p>

<p>
For more information please contact ...</p>
"""
help_page_form = ""
help_page = {}
help_introduction = """
<h3>Introduction</h3>
<p>
Welcome <user>.
</p>
<p>You have successfully logged into the Anchurus-II Web Application.
</p>
<p>
Please select a site. If a site you require access to, is not in the 'Select Site' list, please contact the Site Leader for that site to provide you with access.
<br>Once a site has been selected you can use the menu items to select your actions.</p>
<p>
<b>Note:</b> When changing/selecting a new site, all current active workspaces will be closed.</p>
<h3> </h3>
<p>
For more information on recording Archaeological excavations please go to the
<a href="https://anchurus.co.uk/" target=_blank>Anchurus Website</a></p>
"""
site_introduction = """
<h3>Site Introduction</h3>
<p>
Welcome <user>.
</p>
<p>You have successfully selected a site.
</p>
<p>
You can now check the contents of the database tables by using a List action.
Or use the Query tab to check for any queries you wold like run.</p>
<p>
<b>Note:</b> When changing/selecting a new site, all current active workspaces will be closed.</p>
<h3> </h3>
<p>
For more information on recording Archaeological excavations please go to the
<a href="https://anchurus.co.uk/" target=_blank>Anchurus Website</a></p>
"""