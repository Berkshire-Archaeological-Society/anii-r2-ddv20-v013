import datetime
import re
import time

from anvil import *
import anvil.server
#import anvil.google.auth, anvil.google.drive
#from anvil.google.drive import app_files
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables
#import anvil.users

from .popover import popover, pop


for component in [TextBox, TextArea, DatePicker, DropDown]:
    component.popover = popover
    component.pop = pop


def re_sub(pattern, repl, text):
    texts_1 = text.split('\n')
    texts_2 = [repl] * len(texts_1)
    for n_text in range(len(texts_1)):
        matches = re.match(pattern, texts_1[n_text])
        if matches:
            for n_match, match in enumerate(matches.groups(), 1):
                texts_2[n_text] = texts_2[n_text].replace(f'\\{n_match}', match)
        else:
            texts_2[n_text] = texts_1[n_text]
    return '\n'.join(texts_2)


class Validator:
    """
    component    always required
    error_label  if provided, the label is either hid or made visible and set to either
                 message (if provided) or to a default message
                 if not provided, the error message is shown on a popover (see placement below)
    message      error message that replaces the default error message
    events       list of events that trigger the validation
                 if not provided, then the validation is only executed on demand calling
                 validate(component) or validate_all()
    format       if provided uses the lost_focus event to validate and format the text ('lost_focus'
                 is automatically added to the list of events);
                 it can have these values:
                 phone        formats a ten digit string into (123) 123-1234
                 float 0.2f   convert the value to float, then use standard string.format() formatting syntax
                 $            equivalent to 'float 0.2f'
                 regex@pattern@repl  the 6th character is used as separator, so just use a character
                                     that is not used in the pattern; similar to regex.sub, which
                                     doesn't work in skulpt, but it's close enough; for example this
                                     formats a phone number: 'regex@(\d{3}).*(\d{3}).*(\d{4})@(\1) \2-\3'
    placement    position of the popover when error_label is not provided - can be right, left, top or bottom
                 default is left
    """

    def __init__(self, default_events=None, default_placement='left'):
        self._all_rules = {}
        self._components_with_popover = {}
        self._default_events = default_events or []
        self._default_placement = default_placement

    def _add_to_all_rules(self, component, rule):
        if component in self._all_rules:
            self._all_rules[component].append(rule)
        else:
            self._all_rules[component] = [rule]

        if rule['error_label']:
            rule['error_label'].visible = False

        for e in rule['events']:
            component.add_event_handler(e, self._check_one_component)

        if rule['format'] and 'lost_focus' not in rule['events']:
            component.add_event_handler('lost_focus', self._check_one_component)

    def _check_one_component(self, sender, event_name, **e):
        if not sender.visible:
            return True

        for rule in self._all_rules[sender]:
            if not rule['validating_function']():
                return False

        if event_name == 'lost_focus' and rule['format']:
            format = rule['format']

            if format.startswith('regex'):
                pattern, repl = format[6:].split(format[5])
                formatted_string = re_sub(pattern, repl, sender.text)
                if formatted_string != repl:
                    sender.text = formatted_string

            elif format.startswith('float '):
                sender.text = ('{:' + format[6:] + '}').format(float(sender.text))

            elif format == '$':
                sender.text = ('{:0.2f}').format(float(sender.text))

            elif format == 'phone':
                number_groups = re.search('(\d{3}).*(\d{3}).*(\d{4})', sender.text).groups()
                formatted_number = '({}) {}-{}'.format(number_groups[0], number_groups[1], number_groups[2])
                sender.text = formatted_number

            else:
                rule['error_label'].text = 'Unexpected value in format property'

        return True

    def _set_label(self, is_valid, component, error_label, message, default_message, placement):
        if error_label:
            error_label.visible = not is_valid
            if not is_valid:
                error_label.text = message or default_message
        else:
            if is_valid:
                if component in self._components_with_popover:
                    del self._components_with_popover[component]
                    component.pop('destroy')
            if not is_valid:
                txt = message or default_message
                if component not in self._components_with_popover:
                    component.popover(txt, trigger='manual', placement=placement, auto_dismiss=False)
                    component.pop('show')
                elif self._components_with_popover[component] != txt:
                    component.pop('destroy')
                    component.popover(txt, trigger='manual', placement=placement, auto_dismiss=False)
                    component.pop('show')
                self._components_with_popover[component] = txt

    def hide_all_popovers(self):
        """
        Hide all the popovers, usually used in the form_hide event to make sure no popups are left
        """
        for component in self._all_rules.keys():
            try:
                del self._components_with_popover[component]
                component.pop('destroy')
            except:
                pass

    def are_all_valid(self, focus_on_first_invalid_component=True):
        """
        Run the validation on all the components.
        If they are all valid, return True.
        If one or more are not valid, return False and set the focus on the first non valid one.
        Usually this function is called before saving, and moving the focus helps.
        Sometimes it is called at every change event, and moving the focus could prevent the
        user from editing the current input if another input is invalid.
        """
        focus_already_set = False
        is_valid = True
        for component in self._all_rules.keys():
            one_component_is_valid = self._check_one_component(component, 'are_all_valid')
            if not one_component_is_valid:
                is_valid = False
                if focus_on_first_invalid_component and not focus_already_set:
                    try:
                        component.focus()
                        focus_already_set = True
                    except:
                        pass
        return is_valid

    def between(self, component, min_value, max_value, include_min=False, include_max=False, events=None, error_label=None, message='', required=True, format='', placement=None):
        """Include_min and include_max are False by default"""
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            try:
                x = float(component.text)
                is_valid = min_value <= x if include_min else min_value < x
                is_valid = is_valid and (max_value >= x if include_max else max_value > x)
            except (ValueError, TypeError):
                is_valid = False
            self._set_label(is_valid, component, error_label, message, 'Please enter a value between {} and {}'.format(min_value, max_value), placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def greater_than(self, component, min_value, include_min=False, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            try:
                is_valid = float(component.text) >= min_value if include_min else float(component.text) > min_value
            except (ValueError, TypeError):
                is_valid = False
            self._set_label(is_valid, component, error_label, message, 'Please enter a value greater than {}'.format(min_value), placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def email(self, component, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            is_valid = re.match(r'^\w[\w.-]*@\w+[\w.-]*\.\w+$', component.text)
            self._set_label(is_valid, component, error_label, message, 'Please enter an email address', placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def in_the_future(self, component, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.date:
                return True
            is_valid = component.date and component.date >= datetime.date.today()
            self._set_label(is_valid, component, error_label, message, 'Please enter a date in the future', placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def integer(self, component, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            try:
                is_valid = str(int(component.text)) == component.text
            except (ValueError, TypeError):
                is_valid = False
            self._set_label(is_valid, component, error_label, message, 'Please enter an integer', placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def less_than(self, component, max_value, include_max=False, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            try:
                is_valid = float(component.text) <= max_value if include_max else float(component.text) < max_value
            except (ValueError, TypeError):
                is_valid = False
            self._set_label(is_valid, component, error_label, message, 'Please enter a value less than {}'.format(max_value), placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def longer_than(self, component, length_, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            is_valid = len(component.text) > length_
            self._set_label(is_valid, component, error_label, message, 'Please enter a text longer than {} characters'.format(length_), placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def number(self, component, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            is_valid = False
            if component.text:
                try:
                    float(component.text)
                    is_valid = True
                except (ValueError, TypeError):
                    pass
            self._set_label(is_valid, component, error_label, message, 'Please enter a number', placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def phone_number(self, component, events=None, error_label=None, message='', required=True, format='', placement=None):
        """equivalent to regex(pattern=r'\d{3}.*\d{3}.*\d{4}',
                format='regex@.*(\d{3}).*(\d{3}).*(\d{4})@(\1) \2-\3')
        """
        events = events or self._default_events
        placement = placement or self._default_placement

        self.regex(component,
                   pattern=r'.*\d{3}.*\d{3}.*\d{4}',
                   events=events,
                   error_label=error_label,
                   message=message or 'Please enter a valid phone number',
                   required=required,
                   format=format or 'regex@.*(\d{3}).*(\d{3}).*(\d{4})@(\1) \2-\3')

    def regex(self, component, pattern, events=None, error_label=None, message='', required=True, format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if not required and not component.text:
                return True
            is_valid = re.match(pattern, component.text)
            self._set_label(is_valid, component, error_label, message, 'Please enter a text matching "{}"'.format(pattern), placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'required': required,
                                           'format': format})

    def required(self, component, events=None, error_label=None, message='', format='', placement=None):
        """The component must have a value"""
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            if hasattr(component, 'text'):
                is_valid = component.text not in ['', None]
            elif type(component) is DatePicker:
                is_valid = component.date is not None
            elif type(component) is DropDown:
                is_valid = component.selected_value and component.selected_value in component.items
            else:
                raise Exception('Unexpected component type: {}'.format(type(component)))
            self._set_label(is_valid, component, error_label, message, 'Please enter a value', placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'format': format})

    def with_function(self, component, validating_function, events=None, error_label=None, message='', format='', placement=None):
        events = events or self._default_events
        placement = placement or self._default_placement

        def check_this_component(**e):
            is_valid = validating_function(component)
            self._set_label(is_valid, component, error_label, message, 'Wrong value', placement)
            return is_valid

        self._add_to_all_rules(component, {'validating_function': check_this_component,
                                           'events': events or [],
                                           'error_label': error_label,
                                           'message': message,
                                           'format': format})

if __name__ == "__main__":
    column_panel = ColumnPanel()
    column_panel.set_event_handler(
      "show",
      lambda **e: Notification("oops, validator is a dependency", style="danger", timeout=None).show()
    )
    open_form(column_panel)
