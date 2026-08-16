from ._anvil_designer import HelpTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Global

class Help(HelpTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    
    #print(Global.action)
    Global.help_page_form = self
    user = anvil.users.get_user()
    if Global.action.lower() == "help introduction":
      Global.username = user["email"]
      Global.name = user["firstname"] + " " + user["lastname"]
      message = Global.help_introduction.replace("<user>",Global.name)
      rt = RichText(content=message,format="restricted_html")
      Global.help_page_form.help_page_text.add_component(rt)
    elif Global.action.lower() == "site introduction":
      Global.username = user["email"]
      Global.name = user["firstname"] + " " + user["lastname"]
      message = Global.site_introduction.replace("<user>",Global.name)
      rt = RichText(content=message,format="restricted_html")
      Global.help_page_form.help_page_text.add_component(rt)
      
    #rt = RichText(content=Global.help_introduction,format="restricted_html")
    #self.help_page_text.add_component(rt)
    #self.help_page_text.visible = True
