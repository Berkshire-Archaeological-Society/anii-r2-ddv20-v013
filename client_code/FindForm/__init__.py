from ._anvil_designer import FindFormTemplate
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
from ..ListFinds import ListFinds
from ..Validation import Validator


class FindForm(FindFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    Global.find_items = Global.work_area[Global.current_work_area_name]["items"]
    self.validator = Validator()
    # set validation on fields
    self.validator.regex(
      component=self.Count,
      events=["lost_focus", "change"],
      pattern="^(\d+)$",
      required=False,
      message="Integer value",
    )
    self.validator.regex(
      component=self.ContextId,
      events=['lost_focus', 'change'],
      pattern="^C\d{5}$",
      required=True,
      message="Please enter ContextId starting with a 'C' followed by aaccc, with aa as the area number (01-99) and ccc as the context number (001-999)"
      )
    self.validator.regex(
      component=self.FindId,
      events=["lost_focus", "change"],
      pattern="^F\d{5}|^$",
      required=True,
      message="Please enter FindId starting with a 'F'' followed by aaccc, with aa as the area number (01-99) and ccc as the context number (001-999)",
    )
    self.validator.regex(
      component=self.Description,
      events=["lost_focus", "change"],
      pattern="^[a-zA-Z0-9\s.,?!()-]{0,40}$",
      required=True,
      message="Please enter a short description (max 40 characters)",
    )
    # for all actions set SiteId disabled for editing
    #self.SiteId.text = Global.work_area[Global.current_work_area_name]["site_id"]
    print(Global.find_items)
    self.SiteId.text = Global.site_id
    self.SiteId.enabled = False
    if Global.action == "View Find" or Global.action == "Edit Find":
      #print(Global.find_items)
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.find_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"e")
      # fill fields with values for View or Edit
      self.FindId.text = Global.find_items["FindId"]
      self.ContextId.text = Global.find_items["ContextId"]
      self.FromSample.text = Global.find_items["FromSample"]
      self.FindType.selected_value = Global.find_items["FindType"]
      self.RecordStatus.text = Global.find_items["RecordStatus"]
      Global.selected_material_types = []
      self.cbm_tile.checked = False
      if "CBM Tile" in Global.find_items["Material"]:
        self.cbm_tile.checked = True
      self.cbm_brick.checked = False
      if "CBM Brick" in Global.find_items["Material"]:
        self.cbm_brick.checked = True
      self.cbm_drain_pipe.checked = False
      if "CBM Drain Pipe" in Global.find_items["Material"]:
        self.cbm_drain_pipe.checked = True
      self.cbm_mortar.checked = False
      if "CBM Mortar" in Global.find_items["Material"]:
        self.cbm_mortar.checked = True
      self.stone.checked = False
      if "Stone" in Global.find_items["Material"]:
        self.stone.checked = True
      self.roofing_slate.checked = False
      if "Roofing Slate" in Global.find_items["Material"]:
        self.roofing_slate.checked = True        
      self.flint.checked = False
      if "Flint" in Global.find_items["Material"]:
        self.flint.checked = True
      self.worked_flint.checked = False
      if "Worked Flint" in Global.find_items["Material"]:
        self.worked_flint.checked = True
      self.pottery.checked = False
      if "Pottery" in Global.find_items["Material"]:
        self.pottery.checked = True
      self.clay_pipe.checked = False
      if "Clay Pipe" in Global.find_items["Material"]:
        self.clay_pipe.checked = True
      self.metalwork.checked = False
      if "Metalwork" in Global.find_items["Material"]:
        self.metalwork.checked = True
      self.nails.checked =  False
      if "Nails" in Global.find_items["Material"]:
        self.nails.checked =  True
      self.iron_slag.checked = False
      if "Iron Slag" in Global.find_items["Material"]:
        self.iron_slag.checked = True
      self.glass.checked = False
      if "Glass" in Global.find_items["Material"]:
        self.glass.checked = True
      self.animal_bone.checked = False
      if "Animal Bone" in Global.find_items["Material"]:
        self.animal_bone.checked = False
      self.oyster_shells.checked = False
      if "Oyster Shells" in Global.find_items["Material"]:
        self.oyster_shells.checked = True 
      self.wood.checked = False
      if "Wood" in Global.find_items["Material"]:
        self.wood.checked = True
      self.charcoal.checked = False
      if "Charcoal" in Global.find_items["Material"]:
        self.charcoal.checked = True

      self.Count.text = Global.find_items["Count"]
      self.Weight.text = Global.find_items["Weight"]
      self.Name.text = Global.find_items["Name"]
      self.Description.text = Global.find_items["Description"]
      self.Description_header.text = ("Description (" + str(len(self.Description.text)) + "/255):")
      # in View/Edit disable changing FindId
      self.FindId.enabled = False
    if Global.action == "View Find":
      # disable fields from editing when View
      self.ContextId.enabled = False
      self.FindType.enabled = False
      self.Count.enabled = False
      self.Description.enabled = False
      self.RecordStatus.enabled = False
      self.BoxId.enabled = False
      self.FindGroupId.enabled = False
      self.PackageType.enabled = False
      self.YearStart.enabled = False
      self.YearEnd.enabled = False
      self.DatesAssignedBy.enabled = False
      self.Future.enabled = False
      self.ReferenceCollection.enabled = False
      #
      self.Submit_button.visible = False
    if Global.action == "Add Find":
      # call check_DBAcontrol for existing or new DBAcontrol value
      #Global.find_items["DBAcontrol"] = anvil.server.call("check_DBAcontrol",Global.username,"i")
      self.FindId.text = ""
      self.FindId.enabled = True
      self.ContextId.text = ""
      self.ContextId.enabled = True
      self.Description.text = ""
      self.Description.enabled = True
      self.Description_header.text = ("Description (" + str(len(self.Description.text)) + "/255):")

  def Submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validator.are_all_valid():
      # All fields are filled in correct (I think)
      # collect context form details and then call anvil.server add_context
      Global.find_items["FindId"] = self.FindId.text
      Global.find_items["ContextId"] = self.ContextId.text
      Global.find_items["SiteId"] = self.SiteId.text
      Global.find_items["FromSample"] = self.FromSample.text
      Global.find_items["FindType"] = self.FindType.selected_value
      Global.find_items["RecordStatus"] = self.RecordStatus.text
      Global.selected_material_types = []
      if self.cbm_tile.checked:
        Global.selected_material_types.append("CBM Tile")
      if self.cbm_brick.checked:
        Global.selected_material_types.append("CBM Brick")
      if self.cbm_drain_pipe.checked:
        Global.selected_material_types.append("CBM Drain Pipe")
      if self.cbm_mortar.checked:
        Global.selected_material_types.append("CBM Mortar")
      if self.stone.checked:
        Global.selected_material_types.append("Stone")
      if self.roofing_slate.checked:
        Global.selected_material_types.append("Roofing Slate")
      if self.flint.checked:
        Global.selected_material_types.append("Flint")
      if self.worked_flint.checked:
        Global.selected_material_types.append("Worked Flint")
      if self.pottery.checked:
        Global.selected_material_types.append("Pottery")
      if self.clay_pipe.checked:
        Global.selected_material_types.append("Clay Pipe")
      if self.metalwork.checked:
        Global.selected_material_types.append("Metalwork")
      if self.nails.checked:
        Global.selected_material_types.append("Nails")
      if self.iron_slag.checked:
        Global.selected_material_types.append("Iron Slag")
      if self.glass.checked:
        Global.selected_material_types.append("Glass")
      if self.animal_bone.checked:
        Global.selected_material_types.append("Animal Bone")
      if self.oyster_shells.checked:
        Global.selected_material_types.append("Oyster Shells")
      if self.wood.checked:
        Global.selected_material_types.append("Wood")
      if self.charcoal.checked:
        Global.selected_material_types.append("Charcoal")
      delimiter = ","
      Global.find_items["Material"] = delimiter.join(Global.selected_material_types)
      if self.Count.text == "":
        Global.find_items["Count"] = None
      else:
        Global.find_items["Count"] = int(self.Count.text)
      if self.Weight.text == "":
        Global.find_items["Weight"] = None
      else:
        Global.find_items["Weight"] = self.Weight.text
      Global.find_items["Name"] = self.Name.text
      Global.find_items["Description"] = self.Description.text
      Global.find_items["PackageType"] = self.PackageType.text
      Global.find_items["FindGroupId"] = self.FindGroupId.text
      Global.find_items["BoxId"] = self.BoxId.text
      if self.YearStart.text == "":
        Global.find_items["YearStart"] = None
      else:
        Global.find_items["YearStart"] = self.YearStart.text
      if self.YearEnd.text == "":
        Global.find_items["YearEnd"] = None
      else:
        Global.find_items["YearEnd"] = self.YearEnd.text
      Global.find_items["DatesAssignedBy"] = self.DatesAssignedBy.text
      Global.find_items["ReferenceCollection"] = self.ReferenceCollection.text
      Global.find_items["Future"] = self.Future.text
      # check if ContextId exist in DB
      if anvil.server.call("context_get_details",Global.find_items["SiteId"],Global.find_items["ContextId"]) != []:
        # call server for database update
        msg = "This message text should not be seen. Global.action = " + Global.action
        # print(Global.action
        print(Global.find_items)
        if Global.work_area[Global.current_work_area_name]["action"] == "Add Find":
          ret = anvil.server.call("find_add", Global.find_items)
          # if success then goto list contexts
          if ret[:2] == "OK":
            msg = "The find has been successfully inserted to the database."
          else:
            msg = "The find has not been inserted to the database, because of " + ret
        elif Global.work_area[Global.current_work_area_name]["action"] == "Edit Find":
          ret = anvil.server.call("find_update", Global.find_items)
          # if success then goto list contexts
          if ret[:2] == "OK":
            msg = "The find has been successfully updated in the database."
          else:
            msg = "The find has not been updated in the database, because of " + ret
        alert(content=msg)
      else:
        alert("Unknow Context ID. Please enter a correct Context ID.")
    else:
      alert("Please correct the field(s) with errors before submitting.")
    pass

  def Description_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    self.Description_header.text = ("Description (" + str(len(self.Description.text)) + "/255):")
    pass

  def DatesAssignedBy_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.DatesAssignedBy_header.text = ("Dates Assigned By (" + str(len(self.DatesAssignedBy.text)) + "/100):")
    pass


