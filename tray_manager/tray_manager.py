from pystray import Icon as pystray_Icon, Menu as pystray_Menu, MenuItem as pystray_MenuItem
from typing import Optional, Union
from types import FunctionType, MethodType, LambdaType
from pystray._base import Icon as pystray_Icon_Class
from threading import Thread
from PIL import Image
from enum import Enum
from platform import system as p_system
from os import environ as os_environ
from time import sleep as sleep


class TrayManagerCreationException(Exception):
    def __init__(self, error: OSError) -> None:
        """Exception raised when a Pystray.Icon object cannot be created (Most likelly because one Pystray.Icon object already exists)"""
        self.error = error

    def __str__(self) -> str:
        return f"""Unable to create a Pystray.Icon object, (Most likelly because one Pystray.Icon object already exists. Try to close all instances of TrayManager and try again). Exception : {self.error}"""
    
class MenuAddException(Exception):
    def __init__(self, submenu: 'Submenu') -> None:
        """Exception raised when a menu is added to a submenu"""
        self.submenu = submenu
    
    def __str__(self) -> str:
        return f"""A menu cannot be added to a submenu. Exception raised by "{self.submenu._text}" ({self.submenu})."""
    
class CircularAddException(Exception):
    def __init__(self, submenu: 'Submenu', added_submenu: 'Submenu') -> None:
        """Exception raised when a submenu is added to another submenu that contains the current submenu."""
        self.submenu = submenu
        self.added_submenu = added_submenu

    def __str__(self) -> str:
        return f"""The submenu "{self.submenu._text}" ({self.submenu}) is contained in the submenu "{self.added_submenu._text}" ({self.added_submenu}) that you're trying to add. That is prohibited as it causes a circular add"""

class TooManyDefaultItems(Exception):
    def __init__(self, menu: Union['Menu', 'Submenu'], items: list[Union['Label', 'Button', 'CheckBox', 'Submenu']]) -> None:
        """Exception raised when more than one items has the default option in the same menu/submenu."""
        self.menu = menu

        if len(items) == 2:
            text = f'"{items[0]._text}" ({items[0]}) and "{items[1]._text}" ({items[1]})'
        else:
            text = ''
            for item in items[0: -2]:
                text += f'"{item._text}" ({item}), '
            text += f'"{items[-2]._text}" ({items[-2]}) and "{items[-1]._text}" ({items[-1]})'

        if isinstance(self.menu, Menu):
            self.text =  f"""The menu can't contain more than one item with the default option.\nProblem with : {text}."""
        else:
            self.text =  f"""The submenu "{self.menu._text}" ({self.menu}) can't contain more than one item with the default option.\nProblem with : {text}."""

    def __str__(self) -> str:
        return self.text
            
class UnknownBackend(Exception):
    def __init__(self, backend: str) -> None:
        """Exception raised when the specified backend isn't a correct backend."""
        self.backend = backend

    def __str__(self) -> str:
        return f"""The backend "{self.backend}" isn't a correct backend, please use one of the backend provided by the Backends class"""

class UncompatibleBackend(Exception):
    def __init__(self, os: str, backend: str, os_backends: Union[list['Backends'], 'Backends', None]) -> None:
        """Exception raised when the specified backend isn't supported on the OS."""
        self.os = os
        self.backend = backend
        self.os_backends = os_backends

    def __str__(self) -> str:
        if self.os_backends:
            if isinstance(self.os_backends, list):
                text = "Please use one of the following backends : "
                for backend in range(len(self.os_backends) - 1):
                    text += f"{backend}, "
                text += f"or {self.os_backends[-1]} for {self.os}."
            else:
                text = f"Please use {self.os_backends} for {self.os}."
        else:
            text = "Please use win32 for Windows, darwin for MacOS and gtk, xorg, appindicator or ayatana-appindicator for Linux."
        return f"""The backend "{self.backend}" isn't supported on your OS ({self.os}). {text}"""

class UnsuportedFeature(Exception):
    def __init__(self) -> None:
        """Exception raised when a feature is called but isn't avaible on the OS."""
    
    def __str__(self) -> str:
        os = p_system()
        if os == "":
            os = "Unrecognised OS"
        return f"""The feature isn't supported on your os ({os})."""

class MenuNotSupported(UnsuportedFeature):
    def __init__(self) -> None:
        """Exception raised when the menu feature is called but isn't supported on the OS."""
    
    def __str__(self) -> str:
        os = p_system()
        if os == "":
            os = "Unrecognised OS"
        return f"""The menu feature isn't supported on your OS ({os}). This feature is actually only supported on Windows (backend : win32), MacOS (backend : darwin) and Linux (backend gtk, appindicator and ayatana-appindicator)."""

class DefaultNotSupported(UnsuportedFeature):
    def __init__(self, item: Union['Label', 'Button', 'CheckBox', 'Submenu']) -> None:
        """Exception raised when the default feature is called but isn't supported on the OS."""
        self.item = item

    def __str__(self) -> str:
        os = p_system()
        if os == "":
            os = "Unrecognised OS"
        return f"""The default feature isn't supported on your OS ({os}). This feature is actually only supported on Windows (backend : win32), and Linux (backend : gtk and xorg).\nException raised by "{self.item._text}" ({self.item})."""

class RadioNotSupported(UnsuportedFeature):
    def __init__(self, item: 'CheckBox') -> None:
        """Exception raised when the radio feature is called but is not avaible on the OS."""
        self.item = item

    def __str__(self) -> str:
        os = p_system()
        if os == "":
            os = "Unrecognised OS"
        return f"""The radio feature isn't supported on your OS ({os}). This feature is actually only supported on Windows (backend : win32) and Linux (backend : gtk, xorg, appindicator and ayatana-appindicator).\nException raised by "{self.item._text}" ({self.item})."""

class NotificationNotSupported(UnsuportedFeature):
    def __init__(self) -> None:
        """Exception raised when the notification feature is called but is not availbe on the OS."""
    
    def __str__(self) -> str:
        os = p_system()
        if os == "":
            os = "Unrecognised OS"
        return f"""The notification feature insn't supported on your OS ({os})."""

class Values(Enum):
    """The class containing the custom values used in TrayManager."""
    DEFAULT = "DefaultValue"
    DISABLED = "DisabledValue"

class Backends(Enum):
    """The class containing the backends avaible in TrayManager."""
    WIN32 = "win32"
    GTX = "gtx"
    APP_INDICATOR = "app-indicator"
    AYATANA_APP_INDICATOR = "ayatana-appindicator"
    XORG = "xorg"
    DARWIN = "darwin"


class __OsSupport:
    def __init__(self) -> None:
        """A class used to get the supported features of the current OS."""
        try:
            self.__icon = pystray_Icon("")
        except OSError as e:
            raise TrayManagerCreationException(e)

        self.SUPPORT_MENU = self.__support_menu()
        self.SUPPORT_NOTIFICATION = self.__support_notification()
        self.SUPPORT_RADIO = self.__support_radio()
        self.SUPPORT_DEFAULT = self.__support_default()
    
    def __support_menu(self) -> bool:
        """Check if the OS support the pystray menu."""
        return self.__icon.HAS_MENU
    
    def __support_notification(self) -> bool:
        """Check if the OS support the pystray notifications."""
        return self.__icon.HAS_NOTIFICATION
    
    def __support_radio(self) -> bool:
        """Check if the OS support the pystray radio (Dot look) of CheckBox."""
        return self.__icon.HAS_MENU_RADIO
    
    def __support_default(self) -> bool:
        """Check if the OS support the pystray default option (Bold look and default item)."""
        return self.__icon.HAS_DEFAULT_ACTION



class Notification:
    def __init__(self, tray: 'TrayManager') -> None:
        """A class for managing the notification using pystray's interface.\nThis doesn't seems to work for now, this class is placed under NotImplemented label until the notifications works again"""
        self.tray = tray
        return
    
    def notify(self, title: str, message: str, remove_after_s: float = -1) -> None:
        """Display a notification. This doesn't seems to work for now, this class is placed under NotImplemented label until the notifications works again.\n
        Parameters
        ----------
        * title: str\n
        The title of the notification.
        * message: str\n
        The content of the notification.
        * remove_after_s: float\n
        The delay in seconds to wait before removing the notification, if set to a negative value, doesn't remove the notification."""

        raise NotImplementedError
        if not OsSupport.SUPPORT_NOTIFICATION:
            raise NotificationNotSupported
        
        self.tray.tray.notify(message, title)
        
        if remove_after_s > 0:
            thread = Thread(target=self._delay, args=(remove_after_s,))
            thread.start()
        return

    def remove_notification(self) -> None:
        """Remove a notification. This doesn't seems to work for now, this class is placed under NotImplemented label until the notifications works again."""
        raise NotImplementedError
        self.tray.tray.remove_notification()
        return

    def _delay(self, delay: float) -> None:
        """Private function. Wait a certain amount of time before removing the notification."""
        sleep(delay)
        self.remove_notification()
        return



class Item:
    """The default class for the menu's items."""
    def _update(self: Union['Label', 'Button', 'CheckBox', 'Separator']) -> None:
        """Update the menu if the item that triggered the update is in the menu."""
        if self.tray != None: # Check if tray is defined (tray may not be defined if the item has not been added to the menu or to a submenu that has been added to the menu)
            self.tray: TrayManager
            self.tray.tray.update_menu() # Update the menu
        return

class Label(Item):
    def __init__(self, text: str, default: bool = False) -> None:
        """Create a Label item.\n
        Parameter
        ----------
        * text: str\n
            The text of the label.
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator)."""

        self.tray: Optional[TrayManager] = None

        self._text = text
        self._default = default
        self._item_state = True
        self.item = self.__create_item() # Create our item
        return

    def edit(self, text: str = Values.DEFAULT, default: bool = Values.DEFAULT) -> None:
        """Edit the Label item.\n
        Parameter
        ----------
        * text: str (Facultative)\n
            The text of the label, if not specified, don't change.
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator). If not specified, don't change."""

        if text is not Values.DEFAULT:
            self._text = text
        
        if default is not Values.DEFAULT:
            self._default = default

        self.item = self.__create_item() # Create the new item
        self._update() # Trigger a menu update
        return
    
    def enable(self) -> None:
        """Enable the Label item"""
        self._item_state = True
        self.item = self.__create_item()
        self._update()
        return

    def disable(self) -> None:
        """Disable the Label item"""
        self._item_state = False
        self.item = self.__create_item()
        self._update()
        return
    
    def __create_item(self) -> pystray_MenuItem:
        """Create the pystray_MenuItem Label object."""
        if self._default:
            if not OsSupport.SUPPORT_DEFAULT:
                raise DefaultNotSupported(self)
            
        return pystray_MenuItem(self._text, None, default=self._default, enabled=self._item_state)



class Button(Item):
    def __init__(self, text: str, callback: FunctionType | MethodType | LambdaType | None, args: tuple | None = None, default: bool = False) -> None:
        """Create a Button item.\n
        Parameters
        ----------
        * text: str\n
            The text of the button.
        * callback: FunctionType or MethodType or LambdaType (Facultative)\n
            The function to callback when button is clicked.
        * args: tuple (Facultative)\n
            The arguments to pass to the callback, MUST be a tuple.
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator)."""

        self.tray: Optional[TrayManager] = None
        self._text = text
        self._callback = callback
        self._callback_args = args
        self._default = default
        self._item_state = True
        self.item = self.__create_item() # Create our item
        return
    
    def edit(self, text: str = Values.DEFAULT, callback: FunctionType | MethodType | LambdaType | None = Values.DEFAULT, args: tuple | None = Values.DEFAULT, default: bool = Values.DEFAULT) -> None:
        """Edit the Button item.\n
        Parameters
        ----------
        * text: str (Facultative)\n
            The text of the button, if not specified, don't change.
        * callback: FunctionType or MethodType or LambdaType (Facultative)\n
            The function to callback when button is clicked, if None, don't callback, if not specified, don't change.
        * args: tuple (Facultative)\n
            The arguments to pass to the callback, MUST be a tuple, if not specified, don't change.
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator). If not specified, don't change."""

        # Set new values, if the value is Balues.DEFAUT, don't change
        if text is not Values.DEFAULT:
            self._text = text
    
        if callback is not Values.DEFAULT:
            self._callback = callback

        if args is not Values.DEFAULT:
            self._callback_args = args

        if default is not Values.DEFAULT:
            self._default = default

        self.item = self.__create_item() # Create the new item
        self._update() # Trigger a menu update
        return

    def enable(self) -> None:
        """Enable the Button item"""
        self._item_state = True
        self.item = self.__create_item()
        self._update()
        return

    def disable(self) -> None:
        """Disable the Button item"""
        self._item_state = False
        self.item = self.__create_item()
        self._update()
        return
    
    def __callback(self, tray: pystray_Icon_Class, item: pystray_MenuItem) -> None:
        """Manage the callback of the button."""
        if isinstance(self._callback, FunctionType | MethodType | LambdaType): # Check if the callback is a function
            if isinstance(self._callback_args, tuple): # Check if the args is a tuple
                self._callback(*self._callback_args) # Call the callback with the given arguments

            else:
                self._callback() # Call the callback without arguments
        return

    def __create_item(self)  -> pystray_MenuItem:
        """Create the pystray_MenuItem Button object."""
        if self._default:
            if not OsSupport.SUPPORT_DEFAULT:
                raise DefaultNotSupported(self)
            
        return pystray_MenuItem(self._text, self.__callback, default=self._default, enabled=self._item_state)



class CheckBox(Item):
    def __init__(self, text: str, check_default: bool | None = False, checked_callback: FunctionType | MethodType | LambdaType | None = None, checked_callback_args: tuple | None = None, unchecked_callback: FunctionType | MethodType | LambdaType | None = None, unchecked_callback_args: tuple | None = None, use_radio_look: bool = False, default: bool = False) -> None:
        """Create a CheckBox item.\n
        Parameters
        ----------
        * text: str\n
            The text of the checkbox.
        * check_default: bool | None (Facultative)\n
            The status of the checkbox at start (checked (True) / not checked (False)) if None, the checkmark will not display.
        * checked_callback: FunctionType or MethodType or LambdaType (Facultative)\n
            The function to callback when the checkbox is clicked and switch from unchecked to checked.
        * checked_callback_args: tuple (Facultative)\n
            The arguments to pass to the checked_callback, MUST be a tuple.
        * unchecked_callback: FunctionType or MethodType or LambdaType (Facultative)\n
            The functiion to callback when the checkbox is clicked and switch from checked to unchecked.
        * unchecked_callback_args: tuple (Facultative)\n
            The arguments to pass to the unchecked_callback, MUST be a tuple.
        * use_radio_look: bool (Facultative)\n
            Define if the status of the checkbox should be displayed as a checkmark or a radio (A dot), this is currently not supported on macOS (darwin).
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator)."""


        self.tray: Optional[TrayManager] = None

        self._text = text

        self._checked_callback = checked_callback
        self._checked_callback_args = checked_callback_args
        self._unchecked_callback = unchecked_callback
        self._unchecked_callback_args = unchecked_callback_args
        self._use_radio_look = use_radio_look
        self._default = default
        self._item_state = True

        if check_default == None:
            check_default = False
            disabled = True
        else:
            disabled = False

        self._status =  {"current": None, "requested": check_default, "disabled": disabled} # The dict we'll use to change the checkbox status (The checkmark state of our checkbox)
        self.item = self.__create_item()
        return

    def edit(self, text: str = Values.DEFAULT, check_default: bool | None = Values.DEFAULT, checked_callback: FunctionType | MethodType | LambdaType | None = Values.DEFAULT, checked_callback_args: tuple | None = Values.DEFAULT, unchecked_callback: FunctionType | MethodType | LambdaType | None = Values.DEFAULT, unchecked_callback_args: tuple | None = Values.DEFAULT, use_radio_look: bool = Values.DEFAULT, default: bool = Values.DEFAULT) -> None:
        """Edit the CheckBox item.\n
        Parameters
        ----------
        * text: str (Facultative)\n
            The text of the checkbox, if not specified, don't change.
        * check_default: bool | None (Facultative)\n
            The status of the checkbox at start (checked (True) / not checked (False)) if None, the checkmark will not display, if not specified, don't change.
        * checked_callback: FunctionType or MethodType or LambdaType (Facultative)\n
            The function to callback when the checkbox is clicked and switch from unchecked to checked, if not specified, don't change.
        * checked_callback_args: tuple (Facultative)\n
            The arguments to pass to the checked_callback, MUST be a tuple, if not specified, don't change.
        * unchecked_callback: FunctionType or MethodType or LambdaType (Facultative)\n
            The functiion to callback when the checkbox is clicked and switch from checked to unchecked, if not specified, don't change.
        * unchecked_callback_args: tuple (Facultative)\n
            The arguments to pass to the unchecked_callback, MUST be a tuple, if not specified, don't change.
        * use_radio_look: bool (Facultative)\n
            Define if the status of the checkbox should be displayed as a checkmark or a radio (A dot), this is currently not supported on macOS (darwin).
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator). If not specified, don't change."""
        
        # Set new values, if the value is Balues.DEFAUT, don't change

        if text is not Values.DEFAULT:
            self._text = text

        if check_default is not Values.DEFAULT:
            if check_default == None:
                self._status["disabled"] = True
            else:
                self._status["disabled"] = False
                self._status["requested"] = check_default
        

        if checked_callback is not Values.DEFAULT:
            self._checked_callback = checked_callback
        
        if checked_callback_args is not Values.DEFAULT:
            self._checked_callback_args = checked_callback_args
        
        if unchecked_callback is not Values.DEFAULT:
            self._unchecked_callback = unchecked_callback
        
        if unchecked_callback_args is not Values.DEFAULT:
            self._unchecked_callback_args = unchecked_callback_args
        
        if use_radio_look is not Values.DEFAULT:
            self._use_radio_look = use_radio_look

        if default is not Values.DEFAULT:
            self._default = default

        self.item = self.__create_item() # Create the new item
        self._update() # Trigger a menu update
        return

    def get_status(self) -> bool | None:
        """Return the current status of the checkbox (checked = True, unchecked = False, disabled = None)."""
        return self._status["current"]
    
    def set_status(self, new_status: bool | None) -> None:
        """Set the status of the checkbox.\n
            Parameter
            ----------
            * new_status: bool | None\n
                The new status of the checkbox (checked = True, unchecked = False, disabled = None)."""
        
        if new_status == None:
            self._status["disabled"] = True # Disable the checkbox update (The checkmark of the checkbox update)
        
        else:
            # Set the new value in the dict
            self._status["disabled"] = False
            self._status["requested"] = new_status

        self._update() # Trigger a menu update
        return

    def enable(self) -> None:
        """Enable the CheckBox item"""
        self._item_state = True
        self.item = self.__create_item()
        self._update()
        return

    def disable(self) -> None:
        """Disable the Checkbox item"""
        self._item_state = False
        self.item = self.__create_item()
        self._update()
        return
    
    def __callback(self, tray: pystray_Icon_Class, item: pystray_MenuItem) -> None:
        """Manage the callback and the new status of the checkbox when clicked on in the menu and call callback."""

        if self._status["disabled"]: # If the checkbox is disable don't do anything and return
            return
        
        self._status["current"] = not self._status["current"] # Change the status of the checkbox
        self._update() # Trigger a menu update
        
        if self._status["current"] == True:
            if isinstance(self._checked_callback, FunctionType | MethodType | LambdaType): # Check if the checked_callback is a function
                if isinstance(self._checked_callback_args, tuple): # Check if the args is a tuple
                    self._checked_callback(*self._checked_callback_args) # Call the callback with the given arguments
                else:
                    self._checked_callback() # Call the callback without arguments

        elif self._status["current"] == False:
            if isinstance(self._unchecked_callback, FunctionType | MethodType | LambdaType): # Check if the unchecked_callback is a function
                if isinstance(self._unchecked_callback_args, tuple): # Check if the args is a tuple
                    self._unchecked_callback(*self._unchecked_callback_args) # Call the callback with the given arguments
                else:
                    self._unchecked_callback() # Call the callback without arguments
        return

    def __update_status(self) -> bool:
        """Update the status of the checkbox."""
        if self._status["requested"] != None: # Check if a change a status was requested
            self._status["current"] = self._status["requested"] # Change the status
            self._status["requested"] = None # Set the request to None
        return self._status["current"] # Returns the current status
    
    def __create_item(self) -> pystray_MenuItem:
        """Create the pystray_MenuItem CheckBox object."""
        if self._use_radio_look:
            if not OsSupport.SUPPORT_RADIO:
                raise RadioNotSupported(self)
            
        if self._default:
            if not OsSupport.SUPPORT_DEFAULT:
                raise DefaultNotSupported(self)
            
        return pystray_MenuItem(self._text, self.__callback, lambda item: self.__update_status(), radio=self._use_radio_look, default=self._default, enabled=self._item_state)



class Separator(Item):
    def __init__(self) -> None:
        """Create a Separator item."""

        self.item = pystray_Menu.SEPARATOR # Create the separator item
        self.tray: Optional[TrayManager] = None
        return



class Submenu(Item):
    def __init__(self, text: str, default: bool = False) -> None:
        """Create a Submenu item.\n
        Parameter
        ---------
        * text: str\n
            The text of the submenu.
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator)."""

        self._items: list[Label | Button | CheckBox | Separator | Submenu] = []
        self._text = text
        self._default = default
        self.tray: Optional[TrayManager] = None
        self._item_state = True

        self.__default_item = Label("") # Set the default label to be added when the submenu doesn't contain any displayable item (such as Separators)
        return

    def edit(self, text: str = Values.DEFAULT, default: bool = Values.DEFAULT) -> None:
        """Edit the Submenu item.\n
        Parameter
        ---------
        * text: str (Facultative)\n
            The text of the submenu, if not specified, don't change.
        * default: bool (Facultative)\n
            Define if the item is the default item of that menu (It is drawn in a distinguished style and will be activated as the default item). There can only be one default item by menu. This is currently not supported on MacOs (darwin) and Linux (appindicator and ayatana-appindicator). If not specified, don't change."""
        
        if text is not Values.DEFAULT:
            self._text = text
        
        if default is not Values.DEFAULT:
            self._default = default

        self._update() # Trigger a menu update
        return
    
    def add(self, item: Union[Label, Button, CheckBox, Separator, 'Submenu'], index: int = -1) -> None:
        """Add an item to the submenu.\n 
        Note: You can't add a submenu that contain the current submenu, this is prohibited as it would create a recursion loop.\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to add to the submenu.
        * index: int (Facultative)\n
            The index at which the item is going to be appened (Define the order of the items in the submenu)."""
        
        if isinstance(item, Menu):
            raise MenuAddException(self)
        
        if isinstance(item, Submenu):
            if self.__check_recursion_loop(item): # Verify that their is no circular add
                raise CircularAddException(self, item)

        if self.tray:
            item.tray = self.tray
        
        # Add the item to the submenu
        if index == -1:
            self._items.append(item)
        else:
            self._items.insert(index, item)

        self._update() # Trigger a menu update
        return

    def remove(self, item: Union[Label, Button, CheckBox, Separator, 'Submenu']) -> Union[Label, Button, CheckBox, Separator, 'Submenu'] | None:
        """"Remove an item from the submenu.\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to remove from the submenu."""
        
        try: 
            index = self._items.index(item) # Try to get the item index
        except ValueError:
            return
    
        removed = self._items.pop(index) # Remove the item
        self._update() # Trigger a menu update
        return removed # Return the removed item
    
    def get_items(self) -> list[Union[Label, Button, CheckBox, Separator, 'Submenu']]:
        """Return the items contained in the submenu."""
        return self._items
    
    def enable(self) -> None:
        """Enable the Submenu"""
        self._item_state = True
        self._update()
        return

    def disable(self) -> None:
        """Disable the Submenu"""
        self._item_state = False
        self._update()
        return
    
    def __check_recursion_loop(self, submenu: 'Submenu') -> bool:
        """Check if the submenu is not in the given submenu (Used to detect recursion loop)."""
        for item in submenu.get_items():
            if item == self: # Check if the item is the same self
                return True
            
            if isinstance(item, Submenu):
                if self.__check_recursion_loop(item): # Check recursively if the submenu is in the added submenu
                    return True
        return False
    
    def _create_submenu(self) -> pystray_MenuItem:
        """Create the pystray_MenuItem Submenu object."""
        items: list[Label | Button | CheckBox | Separator | Submenu] = []

        __items_with_default_option: list[Label | Button | CheckBox | Separator | Submenu] = []

        
        for item in self._items:
            if item._default:
                __items_with_default_option.append(item)

            if isinstance(item, Submenu): 
                item.tray = self.tray
                item = item._create_submenu() # Create the pystray_MenuItem of that submenu

            elif isinstance(item, Label) or isinstance(item, Button) or isinstance(item, CheckBox) or isinstance(item, Separator):
                item.tray = self.tray
                item = item.item # Get the pystray_MenuItem of the item

            items.append(item)
        
        if len(__items_with_default_option) > 1:
            raise TooManyDefaultItems(self, __items_with_default_option)
        
        if self._default:
            if not OsSupport.SUPPORT_DEFAULT:
                raise DefaultNotSupported(self)
        
        if len(items) == 0 or all(isinstance(i, Separator) for i in self._items): # Check if the submenu is empty or if all the items in the submenu are not displayable without other items (Such as Separators)
            items.append(self.__default_item.item) # Add the default item to allow the submenu to be displayed
        
        return pystray_MenuItem(self._text, pystray_Menu(*items), default=self._default, enabled=self._item_state)



class Menu:
    def __init__(self, tray: 'TrayManager') -> None:
        """Create the menu in the notification.\n
        Parameter
        ---------
        * tray: TrayManager\n
            A TrayManager instance (A menu object is automatically created when you create a TrayManager object)."""

        self.tray = tray
        self._items: list[Label | Button | CheckBox | Separator | Submenu] = []
        self._default_item = Label("") # Set the default label to be added when the menu doesn't contain any displayable item (such as Separators)
        self._menu_state: bool = True
        return

    def add(self, item: Label | Button | CheckBox | Separator | Submenu, index: int = -1) -> None:
        """Add an item to the menu. Raise MenuNotSupported if the OS doesn't support menu.\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to add to the menu.
        * index: int (Facultative)\n
            The index at which the item is going to be appened (Define the order of the items in the menu)."""
        
        if not OsSupport.SUPPORT_MENU:
            raise MenuNotSupported
        
        item.tray = self.tray

        # Add the item to the menu
        if index == -1:
            self._items.append(item)
        else:
            self._items.insert(index, item)

        self.update() # Trigger a menu update
        return
    
    def remove(self, item: Label | Button | CheckBox | Separator | Submenu) -> Label | Button | CheckBox | Separator | Submenu | None:
        """Remove an item from the menu.\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to remove from the menu."""
        
        item.tray = None # We remove the tray argument to prevent the item from triggering a menu update when the item is edited but is not in the menu

        try:
            index = self._items.index(item) # Try to get the item index
        except ValueError:
            return

        removed = self._items.pop(index) # Remove the item
        self.update() # Trigger a menu update
        return removed # Return the removed item

    def get_items(self) -> list[Label | Button | CheckBox | Separator | Submenu]:
        """Return the items contained in the menu."""
        return self._items
    
    def update(self) -> None:
        """Update the menu."""
        self.tray.tray.update_menu()
        return
    
    def enable(self) -> None:
        """Enable the menu"""
        self._menu_state = True
        self.update()
        return
    
    def disable(self) -> None:
        """Disable the menu"""
        self._menu_state = False
        self.update()
        return
    
    def _create_menu(self) -> list[pystray_MenuItem]:
        """Create the list of items composing the menu."""
        items: list[Label | Button | CheckBox | Separator | Submenu] = []

        __items_with_default_option: list[Label | Button | CheckBox | Separator | Submenu] = []

        for item in self._items:
            if item._default:
                __items_with_default_option.append(item)

            if isinstance(item, Submenu):
                item.tray = self.tray
                item = item._create_submenu() # Create the pystray_MenuItem of that submenu
    
            elif isinstance(item, Label) or isinstance(item, Button) or isinstance(item, CheckBox) or isinstance(item, Separator):
                item.tray = self.tray
                item = item.item # Get the pystray_MenuItem of the item

            items.append(item)
        
        if len(__items_with_default_option) > 1:
            raise TooManyDefaultItems(self, __items_with_default_option)
        
        if (len(items) == 0 or all(isinstance(i, Separator) for i in self._items)): # Check if the menu is empty or if all the items in the menu are not displayable without other items (Such as Separators)
            items.append(self._default_item.item) # Add the default item to allow the menu to be displayed

        if not self._menu_state:
            return []

        return items



class TrayManager:
    def __init__(self, app_name: str, default_show: bool = True, run_in_separate_thread: bool = False, setup: FunctionType | MethodType | LambdaType | None = None, setup_args: tuple | None = None, backend: Backends = None) -> None:
        """Create a pystray.Icon object linked to a Menu() object.\n
            Parameters
            ----------
            * app_name: str\n
                The name of the app in the system tray.
            * default_show: bool (Facultative)\n
                Define if the icon is displayed in the system tray when you create your TrayManager object.
            * run_in_separate_thread: bool (Facultative)\n
                Must be set on false for platform compatibility, if you only target usage on Windows, setting that option to True is safe. Note : using that option combined to setup will result in creating a new thread for the setup function in the newly created thread of this option
            * setup: FunctionType or MethodType or LambdaType (Facultative)\n
                The function to run in a separate thread when the pystray_Icon run (Can be used to run your app while having pystray's loop running in the main thread (Platform compatibility)).
            * setup_args: tuple (Facultative)\n
                The arguments to pass to the setup function when the pystray_Icon run, MUST be a tuple.
            * backend: str (Facultative)\n
                Set this to one of the following backends to use it, if None, automatically select one. Possible backends : for Windows : win32 (Default), for MacOs : darwin (Default) for Linux : gtk, xorg, appindicator (Default), ayatana-appindicator (Default's Fallback)."""

        self.menu = Menu(self) # Create the menu item
        self.notification = Notification(self)
        self._default_icon = Image.new("L", (32, 32), 255) # Create the default icon
        self._icons = {str: Image.Image}

        if backend:
            if isinstance(backend, Backends):
                os = p_system()

                if os == "Linux":
                    avaible_backends = [Backends.AYATANA_APP_INDICATOR, Backends.APP_INDICATOR, Backends.GTX, Backends.XORG]
                    if backend not in avaible_backends:
                        raise UncompatibleBackend(os, backend, avaible_backends)
                    
                elif os == "Darwin":
                    if backend is not Backends.DARWIN:
                        raise UncompatibleBackend(os, backend, Backends.DARWIN)

                elif os == "Windows":
                    if backend is not Backends.WIN32:
                        raise UncompatibleBackend(os, backend, Backends.WIN32)
                    
                else:
                    raise UncompatibleBackend("Unrecognised OS", backend, None)
                
                os_environ["PYSTRAY_BACKEND"] = backend.value

            else:
                raise UnknownBackend(backend)

        if OsSupport.SUPPORT_MENU:
            # Create the pystray_Icon object
            self.tray = pystray_Icon(app_name, self._default_icon, app_name, pystray_Menu(lambda: self.menu._create_menu())) # Here we use lamda to allow the menu to dynamically update
        else:
            self.tray = pystray_Icon(app_name, self._default_icon, app_name, None)
            self.menu = None
            
        if run_in_separate_thread:
            #Run it in different thread (pystray.Icon.run() is a blocking function)
            thread = Thread(target=self.__run, args=(default_show, setup, setup_args))
            thread.start()
        else:
            self.__run(default_show, setup, setup_args) # Run the pystray loop in the main thread
        return

    def set_app_name(self, name: str) -> None:
        """Set the name of the app in the system tray."""
        self.tray.title = name
        return

    def load_icon(self, icon: Image.Image | bytes | str, name: str) -> None:
        """Load an icon from PIL Image object, bytes or path and add it to the icons dict with key 'name'\n
        Parameters
        ----------
        * icon: Image.Image | bytes | str\n
            The image to load in the icons dict
        * name: str\n
            The name (key) of the icon in the icons dict"""
        
        if isinstance(icon, Image.Image):
            self._icons[name] = icon
        else:
            i = Image.open(icon)
            self._icons[name] = i
        return

    def set_icon(self, name: Union[str, Values.DEFAULT], show: bool = True) -> None:
        """Set the icon of the app in the system tray from an icon loaded in the icons dict.\n
            Parameters
            ----------
            * name: str | tray_manager.Values.DEFAULT\n
                The name of the icon to use (key) of the icon in the icons dict, if the name is tray_manager.Values.DEFAULT, set it to the default icon.
            * show: bool (Facultative)\n
                Define if the icon should be displayed in the system tray if it was previously hidden."""

        # Set the icon of the app in the system tray
        if name is Values.DEFAULT:
            self.tray.icon = self._default_icon
        else:
            self.tray.icon = self._icons.get(name, self._default_icon)

        if show: # Show the icon in the system tray
            self.show()
        return

    def show(self) -> None:
        """Show the icon in the system tray."""
        # Show the icon in the system tray
        self.tray.visible = True
        return

    def hide(self) -> None:
        """Hide the icon in the system tray."""
        # Hide the icon in the system tray
        self.tray.visible = False
        return

    def kill(self) -> list[Label | Button | CheckBox | Separator | Submenu]:
        """Kill the pystray_Icon, return the items of the menu as list."""
        
        items = self.menu.get_items() # Get the items of the menu
        self.tray.stop() # Stop the pystray_Icon loop
        return items # Return the items

    def __run(self, default_show: bool, setup: FunctionType | MethodType | LambdaType | None, setup_args: tuple | None) -> None:
        """Run the pystray_Icon object."""

        callback = lambda _: self.__run_callback(default_show, setup, setup_args) # We use lamda _: To avoid the problems related to the number of arguments
        self.tray.run(callback)
        return

    def __run_callback(self, default_show: bool, setup: FunctionType | MethodType | LambdaType | None, setup_args: tuple | None):
        """Manage the callback of the __run function."""
        if default_show:
            self.show()
        else:
            self.hide()
        if isinstance(setup, FunctionType | MethodType | LambdaType):
            if isinstance(setup_args, tuple):
                setup(*setup_args)
            else:
                setup()
        return



# OS support interface
OsSupport = __OsSupport()