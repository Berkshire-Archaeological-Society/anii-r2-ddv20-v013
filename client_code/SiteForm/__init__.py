from ._anvil_designer import SiteFormTemplate
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
from ..ListSites import ListSites
from ..Validation import Validator


class SiteForm(SiteFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

    self.validator = Validator()
    # set validation on fields
    self.validator.regex(
      component=self.SiteId,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9]{0,15}$$",
      required=True,
      message="Please enter a short code (max 15 characters)",
    )  
    self.validator.regex(
      component=self.Name,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9\s.,?!()-]{0,30}$",
      required=True,
      message="Please enter a name (max 30 characters)",
    )
    self.validator.regex(
      component=self.YearStart,
      events=["lost_focus", "change"],
      pattern="^\d{4}$",
      required=True,
      message="Please enter a valid year in YYYY format",
    )
    self.validator.regex(
      component=self.YearEnd,
      events=["lost_focus", "change"],
      pattern="^\d{4}$",
      required=False,
      message="Please enter a valid year in YYYY format",
    )
    self.validator.regex(
      component=self.Address,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9\s.,?!()-]{0,250}$",
      required=True,
      message="Please enter an adress (max 250 characters)",
    )
    self.validator.regex(
      component=self.BNGR,
      events=["lost_focus", "change"],
      pattern="^([STNHOstnho][A-Za-z]\s?)(\d{5}\s?\d{5}|\d{4}\s?\d{4}|\d{3}\s?\d{3}|\d{2}\s?\d{2}|\d{1}\s?\d{1})$",
      required=True,
      message="Please enter BNG coordinates format AA 12345 12345 (max 14 characters)",
    )
    #print(Global.work_area[Global.current_work_area_name]["action"])
    if Global.work_area[Global.current_work_area_name]["action"] == "View Site" or Global.work_area[Global.current_work_area_name]["action"] == "Edit Site":
      # fill fields with values for View or Edit
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.site_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"e")
      self.SiteId.text = Global.site_items["SiteId"]
      self.Name.text = Global.site_items["Name"]
      self.Address.text = Global.site_items["Address"]
      self.YearStart.text = Global.site_items["YearStart"]
      self.YearEnd.text = Global.site_items["YearEnd"]
      self.BNGR.text = Global.site_items["BNGR"]
      self.SurveyMethod.selected_value = Global.site_items["SurveyMethod"]
      self.OriginSGeast.text = Global.site_items["OriginSGeast"]
      self.OriginSGnorth.text = Global.site_items["OriginSGnorth"]
      self.C1Easting.text = Global.site_items["C1Easting"]
      self.C1Northing.text = Global.site_items["C1Northing"]
      self.C1SGeast.text = Global.site_items["C1SGeast"]
      self.C1SGnorth.text = Global.site_items["C1SGnorth"]
      self.C2Easting.text = Global.site_items["C2Easting"]
      self.C2Northing.text = Global.site_items["C2Northing"]
      self.C2SGeast.text = Global.site_items["C2SGeast"]
      self.C2SGnorth.text = Global.site_items["C2SGnorth"]
      self.SGAngle.text = Global.site_items["SGAngle"]
      self.PBSGeast.text = Global.site_items["PBSGeast"]
      self.PBSGnorth.text = Global.site_items["PBSGnorth"]
      self.PBaod.text= Global.site_items["PBaod"]
      self.OriginEasting.text = Global.site_items["OriginEasting"]
      self.OriginNorthing.text = Global.site_items["OriginNorthing"]
      # in View/Edit disable changing ContextId
      self.SiteId.enabled = False
    if Global.work_area[Global.current_work_area_name]["action"] == "View Site":
      # disable fields from editing when View
      self.Name.enabled = False
      self.Address.enabled = False
      self.YearStart.enabled = False
      self.YearEnd.enabled = False
      self.BNGR.enabled = False
      self.SurveyMethod.enabled = False
      self.OriginSGeast.enabled = False
      self.OriginSGnorth.enabled = False
      self.C1Easting.enabled = False
      self.C1Northing.enabled = False
      self.C1SGeast.enabled = False
      self.C1SGnorth.enabled = False
      self.C2Easting.enabled = False
      self.C2Northing.enabled = False
      self.C2SGeast.enabled = False
      self.C2SGnorth.enabled = False
      self.SGAngle.enabled = False
      self.PBSGeast .enabled = False
      self.PBSGnorth .enabled = False
      self.PBaod.enabled = False
      self.OriginEasting.enabled = False
      self.OriginNorthing.enabled = False
      #
      self.Submit_button.visible = False
    if Global.work_area[Global.current_work_area_name]["action"] == "Add Site":
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.site_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"i")
      self.SiteId.text = ""
      self.SiteId.enabled = True
      self.SiteId_header.text = (
        "SiteId (" + str(len(self.SiteId.text)) + "/15):"
      )
      self.Name.text = ""
      self.Name.enabled = True
      self.Name_header.text = (
        "Name (" + str(len(self.Name.text)) + "/30):"
      )
      self.YearStart.text = ""
      self.YearStart.enabled = True
      self.YearEnd.text = ""
      self.YearEnd.enabled = True
      self.Address.text = ""
      self.Address.enabled = True 
      self.Address_header.text = (
        "Address (" + str(len(self.Address.text)) + "/255):"
      )
      self.BNGR.text = ""
      self.BNGR.enabled = True
      self.BNGR_header.text = (
        "BNGR (" + str(len(self.BNGR_header.text)) + "/14):"
      )
      self.SurveyMethod.items = Global.SurveyMethod_options
      self.SurveyMethod.enabled  = True
      self.OriginSGeast.enabled = True
      self.OriginSGnorth.enabled = True
      self.C1Easting.enabled = True
      self.C1Northing.enabled = True
      self.C1SGeast.enabled = True
      self.C1SGnorth.enabled = True
      self.C2Easting.enabled = True
      self.C2Northing.enabled = True
      self.C2SGeast.enabled = True
      self.C2SGnorth.enabled = True
      self.SGAngle.enabled = True
      self.PBSGeast .enabled = True
      self.PBSGnorth .enabled = True
      self.PBaod.enabled = True
      self.OriginEasting.enabled = True
      self.OriginNorthing.enabled = True
      #
      self.Submit_button.visible = True

  def Submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validator.are_all_valid():
      # All fields are filled in correct (I think)
      # collect site form details and then call anvil.server add_site
      Global.site_items["SiteId"] = self.SiteId.text
      Global.site_items["Name"] = self.Name.text
      Global.site_items["Address"] = self.Address.text
      Global.site_items["YearStart"] = self.YearStart.text
      if self.YearEnd.text == "":
        Global.site_items["YearEnd"] = None
      else:
        Global.site_items["YearEnd"] = self.YearEnd.text
      Global.site_items["BNGR"] = self.BNGR.text.replace(" ","")
      Global.site_items["SurveyMethod"] = self.SurveyMethod.selected_value
      Global.site_items["OriginSGeast"] = self.OriginSGeast.text
      Global.site_items["OriginSGnorth"] = self.OriginSGnorth.text
      Global.site_items["C1Easting"] = self.C1Easting.text
      Global.site_items["C1Northing"] = self.C1Northing.text
      Global.site_items["C1SGeast"] = self.C1SGeast.text
      Global.site_items["C1SGnorth"] = self.C1SGnorth.text
      Global.site_items["C2Easting"] = self.C2Easting.text
      Global.site_items["C2Northing"] = self.C2Northing.text
      Global.site_items["C2SGeast"] = self.C2SGeast.text
      Global.site_items["C2SGnorth"] = self.C2SGnorth.text
      Global.site_items["SGAngle"] = self.SGAngle.text
      Global.site_items["PBSGeast"] = self.PBSGeast.text
      Global.site_items["PBSGnorth"] = self.PBSGnorth.text
      Global.site_items["PBaod"] = self.PBaod.text
      Global.site_items["OriginEasting"] = self.OriginEasting.text
      Global.site_items["OriginNorthing"] = self.OriginNorthing.text     
      #
      # call server for database update
      msg = "This message text should not be seen. Action = " + Global.work_area[Global.current_work_area_name]["action"]
      #print(Global.site_items)
      if Global.work_area[Global.current_work_area_name]["action"] == "Add Site":
        #print(Global.site_items)
        ret = anvil.server.call("site_add", Global.site_items)
        # if success then goto list contexts
        if ret[:2] == "OK":
          msg = "The site has been successfully inserted to the database."
        else:
          msg = "The site has not been inserted to the database, because of " + ret
      elif Global.work_area[Global.current_work_area_name]["action"] == "Edit Site":
        ret = anvil.server.call("site_update", Global.site_items)
        # if success then goto list contexts
        if ret[:2] == "OK":
          msg = "The site has been successfully updated in the database."
        else:
          msg = "The site has not been updated in the database, because of " + ret
      alert(content=msg)
    else:
      alert("Please correct the field(s) with errors before submitting.")
    pass

  def SiteId_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.SiteId_header.text = ("SiteId (" + str(len(self.SiteId.text)) + "/15):")
    pass

  def Name_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.Name_header.text = ("Site Name (" + str(len(self.Name.text)) + "/30):")
    pass

  def Address_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.Address_header.text = ("Address (" + str(len(self.Address.text)) + "/250):")
    pass

  def BNGR_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.BNGR_header.text = ("BNGR (" + str(len(self.BNGR.text)) + "/14):")
    pass

