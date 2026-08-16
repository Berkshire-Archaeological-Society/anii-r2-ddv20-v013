from anvil import *
import anvil.server

@property
def indeterminate(self):
  return self._indeterminate

@indeterminate.setter
def indeterminate(self,value):
  js.call_js('indeterminate', self, value)
  self._indeterminate = value

CheckBox.indeterminate = indeterminate
CheckBox._indeterminate = False