from ._anvil_designer import UserFormTemplate
from anvil import *
import re
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Global
from .. import Function
from .. import FunctionsB
from ..validation import Validator

class UserForm(UserFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.tag.password = 'My password'
    self.showhide_password_checkbox_change()
    #
    self.validator = Validator()
    # set validation on fields
    self.user_email_value_error.text = "Enter a correct email format."
    # regex "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" = ^S allows empty string |(or) optional '-' number 1-9999 (no 0's) 
    self.validator.require(
      self.user_email_value,
      ['change', 'lost_focus'],
      lambda tb: re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", tb.text),
      self.user_email_value_error
    )
    self.firstname_error.text = "You must enter a firstname."
    self.validator.require_text_field(self.firstname,self.firstname_error)
    
    self.lastname_error.text = "You must enter a lastname."
    self.validator.require_text_field(self.lastname,self.lastname_error)

    self.initials_error.text = "Please enter the two capital letter initials of the user, followed by a letter or digit."
    self.validator.require(
      self.initials,
      ['change', 'lost_focus'],
      lambda tb: re.fullmatch(r"^[A-Z]{2}[A-Za-z0-9]$", tb.text),
      self.initials_error
    )
    #
    self.user_role_value.items = Global.system_user_role_options
    self.user_status_value.items = Global.user_status_options
    self.title.text = "This form is for inserting a new user"
    if Global.action == "Edit User":
      self.title.text = "This form is for updating details of a user"
      #print(Global.action,Global.user_items["email"])
      self.user_email_value.text = Global.user_items["email"]
      self.user_email_value.enabled = False
      self.user_email_value.foreground = "#ffffff"
      self.user_email_value.background = "#000000"
      # password cannot be changed
      self.password_text_box.enabled = False
      self.password_text_box.foreground = "#ffffff"
      self.password_text_box.background = "#000000"
      self.showhide_password_checkbox.enabled = False
      self.showhide_password_checkbox.visible = False
      #
      self.firstname.text = Global.user_items["firstname"]
      self.lastname.text = Global.user_items["lastname"]
      #print(Global.user_items["systemrole"])
      if Global.user_items["systemrole"] is None:
        self.user_role_value.selected_value = "None"
      else:
        self.user_role_value.selected_value = Global.user_items["systemrole"]
      Global.user_role = Global.user_items["systemrole"]
      if Global.user_items["enabled"]:
        Global.user_status = True
        self.user_status_value.selected_value = "True"
      else:
        Global.user_status = False
        self.user_status_value.selected_value = "False"
      # in "Edit User" disable changing Initials
      self.initials.enabled = False
      self.initials.foreground = "#ffffff"
      self.initials.background = "#000000"
      self.initials.text = Global.user_items["initials"]
  
    #validate 

  def user_role_value_change(self, **event_args):
    """This method is called when an item is selected"""
    #print("Role selected is ",self.user_role_value.selected_value)
    Global.system_user_role = self.user_role_value.selected_value
    pass

  def user_status_value_change(self, **event_args):
    """This method is called when an item is selected"""
    #print("Status selected is ",self.user_status_value.selected_value)
    if self.user_status_value.selected_value == "True":
      Global.user_status = True
    else:
      Global.user_status = False
    pass

  def initials_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    Global.user_initials = self.initials.text
    pass

  def submit_changes_click(self, **event_args):
    """This method is called when the button is clicked"""
    #print("New values for ",Global.user_items["email"], ": ", Global.user_role,Global.user_status)
    self.validator.show_all_errors()
    if self.validator.is_valid() and self.user_status_value.selected_value is not None and self.user_role_value.selected_value is not None:
      #alert("All input values are valid")
      # extract field values fom from
      Global.username = self.user_email_value.text
      Global.password = self.password_text_box.text
      Global.user_firstname = self.firstname.text
      Global.user_lastname = self.lastname.text
      Global.user_initials = self.initials.text
      
      if self.user_status_value.selected_value == "True":
        Global.user_status = True
      else:
        Global.user_status = False
        
      Global.system_user_role = self.user_role_value.selected_value
      msg = ""
      # check if initials is unique if action is not "Edit User"
      if Global.action not in ["Edit User","Edit user","edit user"]:
        msg = anvil.server.call("check_initials",Global.user_initials)
      if msg[:5] == "ERROR":
        alert("This initials string is already in use. Please choose another 3 chars string.")
      else:
        if Global.action in ["Edit User","Edit user","edit user"]: 
          msg = anvil.server.call('system_user_update',Global.username, Global.system_user_role,Global.user_status,Global.user_initials,Global.user_firstname,Global.user_lastname)
        elif Global.action in ["Insert User","Insert user","insert user"]:
          msg = anvil.server.call('system_user_insert',Global.username,Global.password,Global.system_user_role,Global.user_status,Global.user_initials,Global.user_firstname,Global.user_lastname)
        else:
          msg = "Unknown action: " + Global.action
        if msg[0:2] == "OK":
          # action was successful. Close the insert/updare workarea
          print(Global.current_work_area_name)
          print(Global.work_area[Global.current_work_area_name])
          Function.delete_workspace(Global.current_work_area_name)
        n = Notification(msg,timeout=Global.notification_timeout)
        n.show()
    else:
     self.validator.show_all_errors()
     alert("Please make sure all fields that are required have a correct value.")
    pass

  def firstname_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    Global.user_firstname = self.firstname.text
    pass

  def lastname_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    Global.user_lastname = self.lastname.text
    pass

  @handle("showhide_password_checkbox", "change")
  def showhide_password_checkbox_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    if self.showhide_password_checkbox.checked:
      self.password_text_box.text = self.tag.password
      self.password_text_box.hide_text = False
      self.showhide_password_checkbox.text = 'Hide Password'
    else:
      self.password_text_box.hide_text = True
      self.showhide_password_checkbox.text = 'Show Password'
    pass

  @handle("password_text_box", "change")
  def password_text_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.tag.password = self.password_text_box.text
    pass


 

