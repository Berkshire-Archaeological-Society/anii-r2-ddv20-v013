from ._anvil_designer import AnomalyFormTemplate
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
#from ..ListContexts import ListContexts
from ..Validation import Validator


class AnomalyForm(AnomalyFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

    self.validator = Validator()
    # set validation on fields
    self.validator.regex(
      component=self.DigYear,
      events=["lost_focus", "change"],
      pattern="^\d{4}$",
      required=True,
      message="Please enter a valid year in YYYY format",
    )
    self.validator.regex(
      component=self.Thickness,
      events=["lost_focus", "change"],
      pattern="^(\d+-\d+|\d+)$",
      required=False,
      message="Integer value or range in cm",
    )
    self.validator.regex(
      component=self.ContextId,
      events=["lost_focus", "change"],
      pattern="^C\d{5}$",
      required=True,
      message="Please enter ContextId starting with a 'C' followed by aaccc, with aa as the area number (01-99) and ccc as the context number (001-999)",
    )
    self.validator.regex(
      component=self.ContextName,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9\s.,?!()-]{0,40}$",
      message="Please enter a short description (max 40 characters)",
    )
    # for all actions set SiteId disabled for editing
    self.SiteId.text = Global.work_area[Global.current_work_area_name]["site_id"] 
    self.SiteId.enabled = False
    self.context_help_information.text = Global.context_help_information
    self.context_help_information.enabled = False
    # print("ContextForm name: ",Global.current_work_area_name)
    # print("ContextForm action: ",Global.work_area[Global.current_work_area_name]["action"] )
    # print("ContextForm Global.action: ",Global.action)
    if (
      Global.work_area[Global.current_work_area_name]["action"] == "View Context"
      or Global.work_area[Global.current_work_area_name]["action"] == "Edit Context"
    ):
      # fill fields with values for View or Edit
      self.ContextId.text = Global.context_items["ContextId"]
      self.ContextName.text = Global.context_items["ContextName"]
      self.DigYear.text = Global.context_items["DigYear"]
      # Note Context_type is a dropdown, not a text field
      self.ContextType.items = Global.context_types
      self.ContextType.selected_value = Global.context_items["ContextType"]
      areas_list = anvil.server.call("areas_get_summary", Global.work_area[Global.current_work_area_name]["site_id"] )
      areas_options = []
      for x in areas_list:
        areas_options.append(x["AreaId"])
      self.AreaId.items = areas_options
      self.AreaId.selected_value = Global.context_items["AreaId"]
      self.Thickness.text = Global.context_items["Thickness"]
      self.FieldDescription.text = Global.context_items["FieldDescription"]
      self.PostExDescription.text = Global.context_items["PostExDescription"]
      self.ContextName_header.text = (
        "Context Name (" + str(len(self.ContextName.text)) + "/40):"
      )
      self.FieldDescription_header.text = (
        "Field Description (" + str(len(self.FieldDescription.text)) + "/65535):"
      )
      self.PostExDescription_header.text = (
        "Post Excavation Description ("
        + str(len(self.PostExDescription.text))
        + "/65535):"
      )
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.context_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"e")
      # in View/Edit disable changing ContextId
      self.ContextId.enabled = False
    if Global.work_area[Global.current_work_area_name]["action"] == "View Context":
      # disable fields from editing when View
      self.ContextName.enabled = False
      self.DigYear.enabled = False
      self.ContextType.enabled = False
      self.AreaId.enabled = False
      self.Thickness.enabled = False
      self.FieldDescription.enabled = False
      self.PostExDescription.enabled = False
      self.Submit_button.visible = False
    if Global.work_area[Global.current_work_area_name]["action"] == "Add Context":
      self.ContextId.text = ""
      self.ContextId.enabled = True
      self.ContextName.text = ""
      self.ContextName.enabled = True
      self.DigYear.text = ""
      self.DigYear.enabled = True
      # Note Context_type and AreaId are dropdowns, not a text
      self.ContextType.items = Global.context_types
      self.ContextType.selected_value = None
      self.ContextType.enabled = True
      areas_list = anvil.server.call("areas_get_summary", Global.work_area[Global.current_work_area_name]["site_id"] )
      areas_options = []
      for x in areas_list:
        areas_options.append(x["AreaId"])
      self.AreaId.items = areas_options
      self.AreaId.enabled = True
      self.Thickness.text = ""
      self.Thickness.enabled = True
      self.FieldDescription.text = ""
      self.FieldDescription.enabled = True
      self.PostExDescription.text = ""
      self.PostExDescription.enabled = True
      self.ContextName_header.text = (
        "Context Name (" + str(len(self.ContextName.text)) + "/40):"
      )
      self.FieldDescription_header.text = (
        "Field Description (" + str(len(self.FieldDescription.text)) + "/65535):"
      )
      self.PostExDescription_header.text = (
        "Post Excavation Description ("
        + str(len(self.PostExDescription.text))
        + "/65535):"
      )
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.context_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"e")
      self.Submit_button.visible = True

  def Submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validator.are_all_valid():
      # All fields are filled in correct (I think)
      # collect context form details and then call anvil.server add_context
      Global.context_items["ContextId"] = self.ContextId.text
      Global.context_items["SiteId"] = self.SiteId.text
      Global.context_items["ContextName"] = self.ContextName.text
      Global.context_items["DigYear"] = self.DigYear.text
      Global.context_items["AreaId"] = self.AreaId.selected_value
      Global.context_items["ContextType"] = self.ContextType.selected_value
      Global.context_items["Thickness"] = self.Thickness.text
      Global.context_items["FieldDescription"] = self.FieldDescription.text
      Global.context_items["PostExDescription"] = self.PostExDescription.text
      #
      if (self.ContextType.selected_value and self.AreaId.selected_value) is not None:
        # call server for database update
        msg = "This message text should not be seen. Global.action = " + Global.action
        # print(Global.action)
        if Global.work_area[Global.current_work_area_name]["action"] == "Add Context":
          ret = anvil.server.call("context_add", Global.context_items)
          # if success then goto list contexts
          if ret[:2] == "OK":
            msg = "The context has been successfully inserted to the database."
          else:
            msg = "The context has not been inserted to the database, because of " + ret
        elif (
          Global.work_area[Global.current_work_area_name]["action"] == "Edit Context"
        ):
          ret = anvil.server.call("context_update", Global.context_items)
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

  def FieldDescription_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.FieldDescription_header.text = (
      "Field Description (" + str(len(self.FieldDescription.text)) + "/65535):"
    )
    pass

  def PostExDescription_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.PostExDescription_header.text = (
      "Post Excavation Description ("
      + str(len(self.PostExDescription.text))
      + "/65535):"
    )
    pass

  def AnomalyName_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.ContextName_header.text = (
      "Context Name (" + str(len(self.ContextName.text)) + "/40):"
    )
    pass
