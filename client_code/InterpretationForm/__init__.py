from ._anvil_designer import InterpretationFormTemplate
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
from ..ListAreas import ListAreas
from ..Validation import Validator


class InterpretationForm(InterpretationFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.validator = Validator()
    # set validation on fields
    self.validator.regex(
      component=self.AreaId,
      events=["lost_focus", "change"],
      pattern="^A\d{5}$",
      required=True,
      message="Please enter an AreaId in Annnnn format",
    )
    self.validator.regex(
      component=self.Description,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9\s.,?!()-]{0,255}$",
      required=False,
      message="Please enter description (max 255 characters)",
    )
    self.validator.regex(
      component=self.Alias,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9\s.,?!()-]{0,45}$",
      required=False,
      message="Please enter and alias name (max 45 characters)",
    )
    self.validator.integer(
      component=self.BottomLeftEasting,
      events=["lost_focus", "change"],
      required=False,
      message="Please enter the Bottom Left Easting",
    )
    self.validator.integer(
      component=self.BottomLeftNorthing,
      events=["lost_focus", "change"],
      required=False,
      message="Please enter the Bottom Left Northing",
    )
    self.validator.integer(
      component=self.TopRightEasting,
      events=["lost_focus", "change"],
      required=False,
      message="Please enter the Top Right Easting",
    )
    self.validator.integer(
      component=self.TopRightNorthing,
      events=["lost_focus", "change"],
      required=False,
      message="Please enter the Top Right Northing",
    )
    # for all actions set SiteId disabled for editing
    self.SiteId.text = Global.site_id
    self.SiteId.enabled = False
    if (
      Global.work_area[Global.current_work_area_name]["action"] == "View Area"
      or Global.work_area[Global.current_work_area_name]["action"] == "Edit Area"
    ):
      # fill fields with values for View or Edit
      # call check_DBAcontrol for existing or new DBAcontrol value
      Global.context_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"e")
      self.AreaId.text = Global.area_items["AreaId"]
      self.Description.text = Global.area_items["Description"]
      self.Description_header.text = (
        "Description (" + str(len(self.Description.text)) + "/255):"
      )
      self.Alias.text = Global.area_items["Alias"]
      self.Alias_header.text = "Alias (" + str(len(self.Alias.text)) + "/45):"
      self.BottomLeftEasting.text = Global.area_items["BottomLeftEasting"]
      self.BottomLeftNorthing.text = Global.area_items["BottomLeftNorthing"]
      self.TopRightEasting.text = Global.area_items["TopRightEasting"]
      self.TopRightNorthing.text = Global.area_items["TopRightNorthing"]
      # in View/Edit disable changing AreaId
      self.AreaId.enabled = False
    if Global.work_area[Global.current_work_area_name]["action"] == "View Area":
      # disable fields from editing when View
      self.AreaId.enabled = False
      self.Description.enabled = False
      self.Alias.enabled = False
      self.BottomLeftEasting.enabled = False
      self.BottomLeftNorthing.enabled = False
      self.TopRightEasting.enabled = False
      self.TopRightNorthing.enabled = False
      self.Submit_button.visible = False
    if Global.work_area[Global.current_work_area_name]["action"] == "Add Area":
      # call check_DBAcontrol for existing or new DBAcontrol value
      Global.context_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"i")
      self.AreaId.text = ""
      self.AreaId.enabled = True
      self.Description.text = ""
      self.Description.enabled = True
      self.Description_header.text = (
        "Description (" + str(len(self.Description.text)) + "/255):"
      )
      self.Alias.text = ""
      self.Alias.enabled = True
      self.Alias_header.text = "Alias (" + str(len(self.Alias.text)) + "/255):"
      self.BottomLeftEasting.text = ""
      self.BottomLeftEasting.enabled = False
      self.BottomLeftNorthing.text = ""
      self.BottomLeftNorthing.enabled = False
      self.TopRightEasting.text = ""
      self.TopRightEasting.enabled = False
      self.TopRightNorthing.text = ""
      self.TopRightNorthing.enabled = False
      self.Submit_button.visible = True

  def Submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validator.are_all_valid():
      # All fields are filled in correct (I think)
      # collect context form details and then call anvil.server add_context
      Global.area_items["AreaId"] = self.AreaId.text
      Global.area_items["SiteId"] = Global.site_id
      Global.area_items["Description"] = self.Description.text
      Global.area_items["Alias"] = self.Alias.text
      if self.BottomLeftEasting.text == "":
        Global.area_items["BottomLeftEasting"] = None
      else:
        Global.area_items["BottomLeftEasting"] = self.BottomLeftEasting.text
      if self.BottomLeftNorthing.text == "":
        Global.area_items["BottomLeftNorthing"] = None
      else:
        Global.area_items["BottomLeftNorthing"] = self.BottomLeftNorthing.text
      if self.TopRightEasting.text == "":
        Global.area_items["TopRightEasting"] = None
      else:
        Global.area_items["TopRightEasting"] = self.TopRightEasting.text
      if self.TopRightNorthing.text == "":
        Global.area_items["TopRightNorthing"] = None
      else:
        Global.area_items["TopRightNorthing"] = self.TopRightNorthing.text
      #
      # call server for database update
      msg = "This message text should not be seen. Global.action = " + Global.action
      # print(Global.action)
      if Global.work_area[Global.current_work_area_name]["action"] == "Add Area":
        ret = anvil.server.call("area_add", Global.area_items)
        # if success then goto list contexts
        if ret[:2] == "OK":
          msg = "The area has been successfully inserted to the database."
        else:
          msg = "The area has not been inserted to the database, because of " + ret
      elif Global.work_area[Global.current_work_area_name]["action"] == "Edit Area":
        ret = anvil.server.call("area_update", Global.area_items)
        # if success then goto list areas
        if ret[:2] == "OK":
          msg = "The area has been successfully updated in the database."
        else:
          msg = "The area has not been updated in the database, because of " + ret
      alert(content=msg)
    else:
      alert("Please correct the field(s) with errors before submitting.")
    pass

  def Phase_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.Description_header.text = (
      "Description (" + str(len(self.Description.text)) + "/255):"
    )
    pass

  def Alias_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.Alias_header.text = "Alias (" + str(len(self.Alias.text)) + "/255):"
    pass
