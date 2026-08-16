from ._anvil_designer import RowFormvRTTemplate
from anvil import *
import anvil.server
import re
import datetime
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil_extras.Quill import Quill

#from ..Validation import Validator
from ..validation import Validator
from .. import FunctionsB
from .. import Global

class RowFormvRT(RowFormvRTTemplate):
  def input_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    column = event_args["sender"].placeholder
    print("In input_change for column: "+column)
    # add * to column if field is required
    #print(Global.work_area[Global.current_work_area_name]["table_info"])
    if next((item['IS_NULLABLE'] for item in Global.work_area[Global.current_work_area_name]["table_info"] if item['COLUMN_NAME'] == column),0) != "YES":
      col = "* " + "<b>&nbsp"+column+"</b>"
    else:
      col = "&nbsp&nbsp" + "<b>&nbsp"+column+"</b>"

    print("Sender: "+str(type(event_args["sender"])))
    if str(type(event_args["sender"])) == "<class 'anvil_extras.Quill.Quill'>":
      # self.form_fields[column]["header"].text = col + " (" + str(len(self.form_fields[column]["field"].get_html())) + "/" + str(self.form_fields[column]["length"]) + "):"
      #print(self.form_fields[column])
      #print(self.form_fields[column]["header"])
      #print(self.form_fields[column]["field"])
      #print(self.form_fields[column]["length"])
      self.form_fields[column]["header"].content = col + " (" + str(len(self.form_fields[column]["field"].getText())) + "/" + str(self.form_fields[column]["length"]) + "):"
      print(str(self.form_fields[column]["header"].content))

    else:
      if str(type(event_args["sender"])) != "<class 'anvil.DatePicker'>":
        self.form_fields[column]["header"].content = col + " (" + str(len(self.form_fields[column]["field"].text)) + "/" + str(self.form_fields[column]["length"]) + "):"
      print(str(self.form_fields[column]["header"].content))

  pass
  
  def __init__(self, site_id, table_name, data_list, action, page_info, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.site_id = site_id
    # Global.site_id is only None when form called from server side (e.g. printing form)
    if Global.site_id is None:
      # initialise some Globals variables for when the function is called from the server side
      Global.site_id = site_id
      Global.action = "View " + table_name.capitalize()
      Global.current_work_area_name = Global.action
      Global.table_name = table_name
      Global.work_area = {}
      Global.work_area[Global.current_work_area_name] = {}
      #print(data_list)
      Global.work_area[Global.current_work_area_name]["data_list"] = data_list
    else:
      # set table_name to one of "context", "find", from the action Global variable
      #print(Global.table_name)
      #print(Global.work_area[Global.current_work_area_name]["action"])
      Global.table_name = Global.work_area[Global.current_work_area_name]["action"].split(" ")[1].lower()
      # Global.action.split(" ")[1].rstrip("s").lower()
      
    action = Global.action.split(" ")[0].lower()
    
    # Inititalize the validator
    self.validator = Validator()
    
    # we need to find out which table we are dealing with
    self.ws_name.text = Global.current_work_area_name
    self.title.text = "This form is to " + Global.action
    # get table information
    #table_info = anvil.server.call("describe_table",Global.table_name)
   
    # And then we need to create all the fields based on table information 
    # loop over table columns
    self.field_details = {}
    self.form_fields = {}
    #for item in table_info:
    #print(Global.work_area[Global.current_work_area_name]["table_info"])
    for item in Global.work_area[Global.current_work_area_name]["table_info"]:
      #print(item)
      if Global.table_name == "users":
        column_name = item["name"]
        if column_name in Global.ignore_users_columns:
          continue
        column_type = item["type"]
      else:
        column_name = item["COLUMN_NAME"]
        column_type = item["COLUMN_TYPE"]
      # types can be varchar(length),int(length),text,float,double,date
      # type text can be 65535 char so need to be a TextArea, other can be a TextBox
      # create the label and the input field
      if column_type == "text":
        #create TextArea input field for text type
        #input = TextArea(tag=column_name)
        input = Quill(placeholder=column_name,toolbar=Global.Quill_toolbarOptions)
        max_length = 65535
        input.add_event_handler('text_change',self.input_change)
      elif column_type == "date":
        # by default create TextBox fields
        input = DatePicker(placeholder=column_name,format="%Y-%m-%d")
        #input = TextBox(placeholder=column_name)
        # date type is 10 long
        max_length = 10
        # add event handler for when input field is changed to update the character count
        input.add_event_handler('change',self.input_change)
      elif column_type == "string":
        input = TextBox(placeholder=column_name)
        input.add_event_handler('change',self.input_change)
        max_length = 100
      elif column_type == "bool":
        #input = TextBox(placeholder=column_name)
        input = DropDown(items=["True", "False"],placeholder=column_name)
        #input.add_event_handler('change',self.input_change)
        max_length = 5
      elif column_type == "datetime":
        input = TextBox(placeholder=column_name)
        #input.add_event_handler('change',self.input_change)
        max_length = 30
      elif column_name in Global.column_with_dropdown.keys():
        input = DropDown(placeholder=column_name)
        #input.add_event_handler('change',self.input_change)
        max_length = 5
      else:
        # by default create TextBox fields
        input = TextBox(placeholder=column_name)
        # extract length from type
        match = re.search(r'\d+',column_type)
        max_length = int(match.group())
        if column_type.find("decimal") != -1 or column_type.find("float") != -1 or column_type.find("double") != -1:
          # for these data types (decimal, double, float) add 1 to max_length as length does not take into account the decimal point
          # (nor for negative symbol but that is not applicable for us)
          max_length = max_length + 1
        # add event handler for when input field is changed to update the character counth
        input.add_event_handler('change',self.input_change)

      # create input_error label used for validation
      input_error = TextBox(placeholder="Please enter the correct value")
      input_error.visible = False

      # create column header with column_name and column_description in one flowpanel (col_header)
      # add * to column name if inoout for field is mandatory
      if Global.table_name != "users" and item["IS_NULLABLE"] == "YES":
        col = "&nbsp&nbsp"
      else:
        col = "*"
        
      # set specific validation checks for the various fields
      if Global.table_name == "users":
        cname = "name"
        prim_key = True if item[cname] == "email" else False
      else:
        cname = "COLUMN_NAME"
        prim_key = True if item["COLUMN_KEY"] == "PRI"  else False
      # if column is Primary Key or a known special column then make it un-editable when action is View or Edit 
      # if Global.table_name != "site" and ((action == "view") or (action in ["edit"] and item["COLUMN_KEY"] == "PRI") or (action in ["insert"] and item["COLUMN_NAME"] == "SiteId") or column_name in ["DBAcontrol","RegistrationDate"]):
      if (
          not (action in ["insert","add"] and Global.table_name == "site" and item[cname] == "SiteId") and 
          ((action == "view") or (action in ["edit"] and prim_key) or
           (action in ["insert"] and item[cname] == "SiteId") or column_name in ["DBAcontrol","RegistrationDate"])
         ):
      #if ((action == "view") or (action in ["edit"] and item["COLUMN_KEY"] == "PRI") or (action in ["insert"] and item["COLUMN_NAME"] == "SiteId") or column_name in ["DBAcontrol","RegistrationDate"]):
        input.enabled = False
        input.foreground = "#ffffff"
        input.background = "#000000"
      #
      
      # start validaton for fields 
      if column_name in ["YearEnd","YearStart","Year","ContextYear","SurveyYear"]:
        input_error.text = "Enter a correct year format (-2147483648 to 2147483647)"
        input_error.foreground ="#FF0000"
        # regex "^(-?[0-9]{1,10}|)$" = any number between -2147483648 to 2147483647; empty string allowed
        # 
        self.validator.require(
          input,
          ['change', 'lost_focus'],
          lambda tb: re.fullmatch(r"^$|^(-?[0-9]{1,10}|)$", tb.text),
          input_error
        )

      elif column_name[-2:] == "Id" and col == "*": # Any column name ending with "Id" that is not "*" (required)
        input_error.text = "You have to enter an Id"
        input_error.foreground ="#FF0000"
        # 
        self.validator.require_text_field(input,input_error)

      #elif column_name in ["Year","ContextYear","SurveyYear"]:   
      #  input_error.text = "Enter a correct year format ((-2147483648 to 2147483647))"
      #  input_error.foreground ="#FF0000"
      #  # regex "^(\d{4}|)$" = 4 digit number (year); empty string allowed 
      #  # 
      #  self.validator.require(
      #    input,
      #    ['change', 'lost_focus'],
      #    lambda tb: re.fullmatch(r"^(\d{4}|)$", tb.text),
      #    input_error
      #  )

      elif column_name in ["Email"]:
        input_error.text = "You must enter an email address"
        input_error.foreground ="#FF0000"
        # regex "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" = valid email address
        self.validator.require(
          input,
          ['change', 'lost_focus'],
          lambda tb: re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", tb.text),
          input_error
        )
        
      elif column_type.find("int") != -1:
        input_error.text = "Please enter a valid whole number"
        input_error.foreground ="#FF0000"
        # 
        self.validator.require(
          input,
          ['change', 'lost_focus'],
          lambda tb: re.fullmatch(r"^$|^\d*$", tb.text),
          input_error
        )

      elif column_type.find("decimal") != -1 or column_type.find("float") != -1 or column_type.find("double") != -1:
        dec_type = re.findall(r'\d+',column_type)
        # regex ^\d{0,x}\.?\d{1,y}
        pattern_string = "^$|^\d{0," + str(int(dec_type[0])-int(dec_type[1])) + "}\.?\d{1," + str(int(dec_type[1])) + "}$"
        #print(dec_type[0],dec_type[1])
        input_error.text = "Please enter a valid number in the form " + "x" * (int(dec_type[0]) - int(dec_type[1])) + "." + "x" * int(dec_type[1])
        input_error.foreground ="#FF0000"
        # 
        self.validator.require(
          input,
          ['change', 'lost_focus'],
          lambda tb: re.fullmatch(pattern_string, tb.text),
          input_error
        )
      
      elif column_name in ["RecordStatus"]:
        # 1. Define your allowed words
        allowed_words = ['Registered','Planned','Dated','Grouped','Report']
        # 2. Build the "OR" part of the rgex: 
        choices = r'(?:' + '|'.join(map(re.escape, allowed_words)) + r')'
        # 3. Assemble the full pattern
        # Starts with a choice, followed by zero or more (comma + choice)
        pattern_string = rf'^{choices}(?:\s*,\s*{choices})*$'
        input_error.text = "You must enter a list of " + str(allowed_words)
        input_error.foreground ="#FF0000"
        self.validator.require(
          input,
          ['change', 'lost_focus'],
          lambda tb: re.fullmatch(pattern_string, tb.text),
          input_error
        )

      elif column_name in Global.column_with_dropdown.keys():
        # 1. Define your allowed options for the DropDown
        input.items = Global.column_with_dropdown[column_name]["options"]
        input.include_placeholder = True 
        input.placeholder = Global.column_with_dropdown[column_name]["placeholder"]
        # 2. Configure the error label
        input_error.text = Global.column_with_dropdown[column_name]["error"]
        input_error.foreground = "#FF0000"
        # 3. Use the validator to check the selected_value
        self.validator.require(
          input,
          ['change'],
          lambda dd: dd.selected_value is not None,
          input_error
        ) 
      elif col == "*" and str(type(input)) != "<class 'anvil_extras.Quill.Quill'>": # this means the columns is required and has not yet been caught by previous checks
        # exclude Quill component as we cannot add the validator for this.
        input_error.text = "This field is required"
        input_error.foreground ="#FF0000"
        # 
        self.validator.require_text_field(input,input_error)

      # end of validation 
      
      # spedial case when Field is RegistrationDate: Pre-fill is for Insert and also block edit contents
      cur_len = 0
      #print(column_name)
      if action in ["insert","add"] and column_name == "RegistrationDate":
        # force RegistrationDate
        input.text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        input.enabled = False
        input.foreground = "#ffffff"
        input.background = "#000000"

      # if action is View or Edit then fill all fields
      if action in ["edit","update","view"]:
        #print(Global.work_area[Global.current_work_area_name]["data_list"][0])
        if str(type(input)) == "<class 'anvil_extras.Quill.Quill'>":
          text = Global.work_area[Global.current_work_area_name]["data_list"][0][column_name]

          # Manually create the Delta instead of using the clipboard
          delta = {"ops": [{"insert": text}]}
          # Apply it
          input.setContents(delta, 'silent')

          cur_len = 0
          if text is not None:
            cur_len = len(text)
          if action == "view":
            input.enable(False)
            input.background = "#052014CC"
        elif str(type(input)) == "<class 'anvil.DatePicker'>":
          input.date = Global.work_area[Global.current_work_area_name]["data_list"][0][column_name]
        elif str(type(input)) == "<class 'anvil.DropDown'>":
          input.selected_value = Global.work_area[Global.current_work_area_name]["data_list"][0][column_name]
        else:
          #print(Global.work_area[Global.current_work_area_name]["data_list"])
          input.text = Global.work_area[Global.current_work_area_name]["data_list"][0][column_name]
          if input.text == "None":
            input.text = ""
            cur_len = 0
          if input.text is not None:
            cur_len = len(input.text)
            
      if Global.table_name.lower() != "site" and column_name == "SiteId" and action in ["edit","insert","add"]: # pre-set SiteId when
        #print("In RowForm. Column name, action, siteId : "+column_name+" "+action+" "+Global.site_id)
        #print(Global.work_area[Global.current_work_area_name]["data_list"][0])
        Global.work_area[Global.current_work_area_name]["data_list"][0][column_name] = Global.site_id
        input.text = Global.work_area[Global.current_work_area_name]["data_list"][0][column_name]
        #print(input.text)
        if input.text == "None":
          input.text = ""
          cur_len = 0
        if input.text is not None:
          cur_len = len(input.text)

      if Global.table_name.lower() == "site" and column_name == "SiteId" and action in ["insert","add"]:
        # for Table site make sure that SiteId column field is empty when action is insert,add
        input.text = "" 
        cur_len = 0
        
      col = col + "<b>&nbsp"+column_name+"</b>" + " (" + str(cur_len) + "/" + str(max_length) + "):" 
      #lab = Label(text=col,font_size=14,tag=column_name)
      lab = RichText(content=col,font_size=14,tag=column_name,format='restricted_html')
      col_comment = "" if Global.table_name == "users" else item["COLUMN_COMMENT"]
      col_description = Label(text=col_comment,font_size=14)
      col_header = FlowPanel()
      col_header.add_component(lab)
      col_header.add_component(col_description)
      # add columns details to nested dictionary
      field_details = {"header": lab, "description": col_description,"field": input, "length": max_length}
      self.form_fields[column_name] = field_details
      # add col_header and input field to column_panel
      # do not add an input field for DBAcontrol column if table is not dbdiary
      if Global.table_name == "dbdiary" or column_name != "DBAcontrol" : 
        self.column_panel_1.add_component(col_header,full_width_row=True)
        self.column_panel_1.add_component(input,full_width_row=True)
        self.column_panel_1.add_component(input_error,full_width_row=True)
    # endof forloop item in table_info
    
    # Add a Submit button if Edit or Add action
    if action in ["edit","add","insert"]:     #"Edit Context","Edit Find","Add Context","Add Find"]:
      submit_btn = Button(text="Submit",role="outlined-button")
      submit_btn.add_event_handler("click",self.submit_btn_click)
      self.column_panel_1.add_component(submit_btn)

    # Add a Execute SQL command button if View Query
    #if Global.action in ["View Query","View query"]:     
    #  execute_sql_btn = Button(text="Execute SQL command",role="outlined-button")
    #  execute_sql_btn.add_event_handler("click",self.execute_sql_btn_click)
    #  self.column_panel_1.add_component(execute_sql_btn)
    # For this work_area form the page_info details are all set to 0; this is for when the server print function calls this form
    Global.work_area[Global.current_work_area_name]["page_info"] = {"page_num": 0, "rows_per_page": 0, "total_rows": 0}

  def execute_sql_btn_click(self, **event_args):
    #print("Execute SQL command button pressed")
    formfields = self.form_fields.items()
    # SQL_Command is a <class 'anvil_extras.Quill.Quill'> object as it is a text datatype so needs to get the test with the Quill method getText()
    Global.query_info = formfields
    Global.query_id = next((str(item[1]['field'].text) for item in list(formfields) if item[0] == "QueryId"),0)
    command = next((str(item[1]['field'].getText()) for item in list(formfields) if item[0] == "SQL_command"),0)
    #print(command)
    if command != "":
      msg, data_list, column_order, Global.tmp_table_info = anvil.server.call("execute_sql_command",command)
      #print(data_list)
      #print(column_order)
      #print(Global.tmp_table_info)
    else:
      msg = "FAIL: SQL command field is empty."
    #print("after execute_sql_commnd")
    #print(Global.tmp_table_info)
    # Check msg for succes or FAIL
    if msg[0: 4] == "FAIL":
      alert(msg)
    else:
      # SQL command completed successfully and returned a data_list. Create a new TableList workspace
      #print(msg)
      Global.column_order = column_order
      Global.table_items = data_list
      Global.table_name = "qresult"
      Global.action = "List " + Global.table_name.capitalize()
      if Global.main_form:  # Important to check if the form exists
        # Create new work_area "View Context" and set focus on this new work_area
        #print("From repatingPanel row calling create_new_work_area for:",Global.action)
        Global.main_form.create_new_work_area(Global.action)
      else:
        print("Main form not found!")

    pass
    
  def submit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    #print("Submit button clicked: ",Global.action)
    action = Global.action.split(" ")[0].lower()
    table_name = Global.action.split(" ")[1].lower()
    self.validator.show_all_errors()
    if self.validator.is_valid():
      # all validated input fields are ok
      row_list = {}
      for col in self.form_fields.items():
        #print(col)
        # Add Additional field validation (if needed) before submitting 
        #print(str(type(col[1]["field"])))
        if str(type(col[1]["field"])) == "<class 'anvil_extras.Quill.Quill'>":
          # at the moment we only get the text of the Quill data, not the full rich text format - need extra column for that
          row_list[col[0]] = col[1]["field"].getText()
          #delta = col[1]["field"].getContents()
          #print("Quill Value is: ",row_list[col[0]])
          #row_list[col[0]] = col[1]["field"].clipboard.convert(text)
          #Global.work_area[Global.current_work_area_name]["data_list"][0][column_name]
          #delta = col[1]["field"].clipboard.convert(text)
          #col[1]["field"].setContents(delta, 'silent')
          #cur_len = 0
          #if text is not None:
            #cur_len = len(text)
        elif str(type(col[1]["field"])) == "<class 'anvil.DatePicker'>":
          row_list[col[0]] = col[1]["field"].date
        elif str(type(col[1]["field"])) == "<class 'anvil.DropDown'>":
          row_list[col[0]] = col[1]["field"].selected_value
        elif str(type(col[1]["field"])) == "<class 'anvil.TextBox'>":
          row_list[col[0]] = col[1]["field"].text
        
        # set empty fields to None
        if row_list[col[0]] in ["","\n"]:
          row_list[col[0]] = None
      #
      #print(Global.action, table_name, row_list)
      #
      if action in ["add","insert"]:
        ret = anvil.server.call("row_insert",table_name,row_list)
        # if success then goto list contexts
        if ret[:2] == "OK":
          msg = "Row has been successfully inserted to the database."
          # if a site has been added, update the site selection dropdown
          if table_name == "site":
            Global.site_options = FunctionsB.set_select_site_dropdown_options() 
            Global.select_site_dropdown.items = Global.site_options.keys()
        else:
          msg = "Row has not been inserted to the database, because of " + ret
      elif action in ["edit","update"]:
        ret = anvil.server.call("row_update",table_name,row_list)
        # if success then goto list contexts
        if ret[:2] == "OK":
          msg = "Row has been successfully updated in the database."
        else:
          msg = "Row has not been updated in the database, because of " + ret
      else:
        msg = "Unknown action: " + action
      alert(content=msg)
     
    else:
      self.validator.show_all_errors()
      alert("There are errors in the form input")
    
    pass

  # a previous version of the submit function; to be check and moved relevant bits to current submit_btn_click function
  def submit_button_click(self, **evemt_args):
    if self.validator.are_all_valid():
      # All fields are filled in correct (I hope ;))
      # collect form details and then call anvil.server add_context
      Global.context_items["ContextId"] = self.ContextId.text
      Global.context_items["SiteId"] = self.SiteId.text
      Global.context_items["Name"] = self.Name.text
      Global.context_items["Year"] = self.Year.text
      #Global.context_items["AreaId"] = self.AreaId.selected_value
      Global.context_items["AreaId"] = self.AreaId.text
      Global.context_items["RecordStatus"] = self.RecordStatus.text
      Global.context_items["FillOf"] = self.FillOfFindId.text
      Global.context_items["ContextType"] = self.ContextType.selected_value
      Global.context_items["Description"] = self.Description.text
      Global.context_items["Interpretation"] = self.Interpretation.text
      Global.context_items["DatesAssignedBy"] = self.DatesAssignedBy.text
      Global.context_items["YearStart"] = self.YearStart.text
      Global.context_items["YearEnd"] = self.YearEnd.text
      #
      if (self.ContextType.selected_value) is not None:
        # call server for database update
        # set all empty fields to None (will be Null in DB)
        for x in Global.context_items:
          if Global.context_items[x] == "":
            Global.context_items[x] = None
        msg = "This message text should not be seen. Global.action = " + Global.action
        #print(Global.action)
        if Global.work_area[Global.current_work_area_name]["action"] == "Add Context":
          ret = anvil.server.call("context_add",Global.context_items)
          # if success then goto list contexts
          if ret[:2] == "OK":
            msg = "The context has been successfully inserted to the database."
          else:
            msg = "The context has not been inserted to the database, because of " + ret
        elif Global.work_area[Global.current_work_area_name]["action"] == "Edit Context":
          ret = anvil.server.call("context_update",Global.context_items)
          # if success then goto list contexts
          if ret[:2] == "OK":
            msg = "The context has been successfully updated in the database."
          else:
            msg = "The context has not been updated in the database, because of " + ret
        alert(content=msg)
      else:
        alert("Please select a value for Contect Type and/or Area ID.")
    else:
      # check which fields are incorrect
      alert("Please correct the field(s) with errors before submitting.")
    pass