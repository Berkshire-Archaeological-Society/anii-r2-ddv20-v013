from ._anvil_designer import ContextFormTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import datetime
from .. import Global
from ..ListContexts import ListContexts
from ..Validation import Validator

class ContextForm(ContextFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    Global.context_items = Global.work_area[Global.current_work_area_name]["items"]
    self.validator = Validator()
    # set validation on fields
    self.validator.regex(component=self.ContextId,
                         events=['lost_focus', 'change'],
                         pattern="^C\d{5}$",
                         required=True,
                         message="Please enter ContextId starting with a 'C' followed by aaccc, with aa as the area number (01-99) and ccc as the context number (001-999)")
    self.validator.regex(component=self.Name,
                         events=['lost_focus', 'change'],
                         pattern="^[a-zA-Z0-9\s.,?!()-]{0,40}$",
                         message="Please enter a short description (max 40 characters)")
    self.validator.regex(component=self.AreaId,
                         events=['lost_focus', 'change'],
                         pattern="^A\d{5}$",
                         required=True,
                         message="Please enter AreaId starting with a 'A' followed by nnnnn (00001-99999)")
    # for all actions set SiteId disabled for editing
    self.validator.regex(component=self.Year,
                         events=['lost_focus', 'change'],
                         pattern="^\d{4}$",
                         required=True,
                         message="Please enter a valid year in YYYY format")
    self.validator.regex(component=self.YearStart,
                         events=['lost_focus', 'change'],
                         pattern="^-?\d{1,4}(?:BC|AD)?$",
                         required=False,
                         message="Please enter a valid year YYYY BC|AD (or -YYYY for BC year)")
    self.validator.regex(component=self.YearEnd,
                           events=['lost_focus', 'change'],
                           pattern="^-?\d{1,4}(?:BC|AD)?$",
                           required=False,
                           message="Please enter a valid year YYYY BC|AD (or -YYYY for BC year)")
    #
    print(Global.context_items)
    self.SiteId.text = Global.site_id
    #Global.work_area[Global.current_work_area_name]["site_id"] 
    self.SiteId.enabled = False
    self.context_help_information.text = Global.context_help_information
    self.context_help_information.enabled = False
    #print("ContextForm name: ",Global.current_work_area_name)
    #print("ContextForm action: ",Global.work_area[Global.current_work_area_name]["action"] )
    #print("ContextForm Global.action: ",Global.action)
    if Global.work_area[Global.current_work_area_name]["action"] == "View Context" or Global.work_area[Global.current_work_area_name]["action"] == "Edit Context":
      # fill fields with values for View or Edit
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.context_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"e")
      self.ContextId.text = Global.context_items["ContextId"]
      self.Name.text = Global.context_items["Name"]
      self.Year.text = Global.context_items["Year"]
      # Note Context_type is a dropdown, not a text field
      self.ContextType.items = Global.context_types
      self.ContextType.selected_value = Global.context_items["ContextType"]
      #areas_list = anvil.server.call('get_areas_summary',Global.site_id)
      #areas_options = []
      #for x in areas_list:
      #  areas_options.append(x["AreaId"])
      #self.AreaId.items = areas_options
      #self.AreaId.selected_value = Global.context_items["AreaId"]
      self.AreaId.text = Global.context_items["AreaId"]
      self.RecordStatus.text = Global.context_items["RecordStatus"]
      self.FillOfFindId.text = Global.context_items["FillOf"]
      self.Description.text = Global.context_items["Description"]
      self.Interpretation.text = Global.context_items["Interpretation"]
      self.Name_header.text = "Context Name (" + str(len(self.Name.text)) + "/40):"
      self.Description_header.text = "Description (" + str(len(self.Description.text)) + "/65535):"
      self.Interpretation_header.text = "Interpretation (" + str(len(self.Interpretation.text)) + "/65535"
      self.YearStart.text = Global.context_items["YearStart"]
      self.YearEnd.text = Global.context_items["YearEnd"]
      self.DatesAssignedBy_header.text = "Dates Assigned By (" + str(len(self.DatesAssignedBy.text)) + "/100):"
      # in View/Edit disable changing ContextId
      self.ContextId.enabled = False
    if Global.work_area[Global.current_work_area_name]["action"] == "View Context":
      # disable fields from editing when View
      self.Name.enabled = False
      self.Year.enabled = False
      self.ContextType.enabled = False
      self.AreaId.enabled = False
      self.RecordStatus.enabled = False
      self.FillOfFindId.enabled = False
      self.Description.enabled = False
      self.Interpretation.enabled = False
      self.YearStart.enabled = False
      self.YearEnd.enabled = False
      self.DatesAssignedBy.enabled = False
      self.Submit_button.visible = False  
    if Global.work_area[Global.current_work_area_name]["action"] == "Add Context":
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.context_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"i")
      self.ContextId.text = ""
      self.ContextId.enabled = True
      self.Name.text = ""
      self.Name.enabled = True
      self.Year.text = ""
      self.Year.enabled = True
      # Note Context_type and AreaId are dropdowns, not a text 
      self.ContextType.items = Global.context_types
      self.ContextType.selected_value = None
      self.ContextType.enabled = True
      #areas_list = anvil.server.call('areas_get_summary',Global.site_id)
      #areas_options = []
      #for x in areas_list:
      #  areas_options.append(x["AreaId"])
      #self.AreaId.items = areas_options
      self.AreaId.text = ""
      self.AreaId.enabled = True
      self.RecordStatus.text = ""
      self.RecordStatus.enabled = True
      self.FillOfFindId.text = ""
      self.FillOfFindId.enabled = True
      self.Description.text = ""
      self.Description.enabled = True
      self.Interpretation.text = ""
      self.Interpretation.enabled = True
      self.Name_header.text = "Context Name (" + str(len(self.Name.text)) + "/40):"
      self.Description_header.text = "Description (" + str(len(self.Description.text)) + "/65535):"
      self.Interpretation_header.text = "Interpretation (" + str(len(self.Interpretation.text)) + "/65535):"
      self.YearStart.text = ""
      self.YearStart.enabled = True
      self.YearEnd.text = ""
      self.YearEnd.enabled = True
      self.DatesAssignedBy_header.text = "Dates Assigned By (" + str(len(self.DatesAssignedBy.text)) + "/100):"
      self.Submit_button.visible = True  

  def Submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validator.are_all_valid():
      # All fields are filled in correct (I think)
      # collect context form details and then call anvil.server add_context
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
      alert("Please correct the field(s) with errors before submitting.")
    pass

  def Name_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.Name_header.text = "Context Name (" + str(len(self.Name.text)) + "/40):"
    pass

  def Description_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.Description_header.text = "Description (" + str(len(self.Description.text)) + "/65535):"
    pass

  def Interpretation_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.Interpretation_header.text = "Interpretation (" + str(len(self.Interpretation.text)) + "/65535):"
    pass

  def DatesAssignedBy_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.DatesAssignedBy_header.text = "Dates Assigned By (" + str(len(self.DatesAssignedBy.text)) + "/100):"
    pass

  def RecordStatus_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.RecordStatus_header.text = "Records Status (" + str(len(self.RecordStatus.text)) + "/25):"
    pass

