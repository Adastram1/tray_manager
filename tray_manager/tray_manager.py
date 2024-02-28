from pystray import Icon as pystray_Icon, Menu as pystray_Menu, MenuItem as pystray_MenuItem
from typing import Optional, Union
from types import FunctionType
from pystray._base import Icon
from threading import Thread
from PIL import Image
from enum import Enum



class CircularAddException(Exception):
    def __init__(self, submenu: 'Submenu', added_submenu: 'Submenu') -> None:
        """Exception raised when a submenu is added to another submenu that contains the current submenu."""
        self.submenu = submenu
        self.added_submenu = added_submenu

    def __str__(self) -> str:
        return f"""The submenu "{self.submenu.text}" ({self.submenu}) is already contained in the submenu "{self.added_submenu.text}" ({self.added_submenu}) that you're trying to add"""



class Values(Enum):
    """The class containing the custom values used in TrayManager"""
    DEFAULT = "DefaultValue"
    DISABLED = "DisabledValue"



class Item:
    """The default class for the menu's items"""

    def _update(self: Union['Label', 'Button', 'CheckBox', 'Separator']) -> None:
        """Update the menu"""
        if self.tray != None: # Check if tray is defined (tray may not be defined if the item has not been added to the menu or to a submenu that has been added to the menu)
            self.tray: TrayManager
            self.tray.tray.update_menu() # Update the menu
        return



class Label(Item):
    def __init__(self, text: str) -> None:
        """Create a Label item\n
        Parameter
        ----------
        * text: str\n
            The text of the label"""

        self.tray: Optional[TrayManager] = None
        
        self.text = text
        self.item = self.__create_item() # Create our item
        return

    def edit(self, text: str) -> None:
        """Edit the Label item\n
        Parameter
        ----------
        * text: str\n
            The text of the label"""

        self.text = text
        self.item = self.__create_item() # Create the new item
        self._update() # Trigger a menu update
        return

    def __create_item(self) -> pystray_MenuItem:
        """Create the pystray_MenuItem Label object"""
        return pystray_MenuItem(self.text, None)



class Button(Item):
    def __init__(self, text: str, callback: FunctionType | None, args: tuple | None = None) -> None:
        """Create a Button item\n
        Parameters
        ----------
        * text: str\n
            The text of the button
        * callback: FunctionType (Facultative)\n
            The function to callback when button is clicked\n
        * args: tuple (Facultative)\n
            The arguments to pass to the callback, MUST be a tuple"""

        self.tray: Optional[TrayManager] = None
        self.text = text
        self.callback = callback
        self.callback_args = args
        self.item = self.__create_item() # Create our item
        return
    
    def edit(self, text: str = Values.DEFAULT, callback: FunctionType | None = Values.DEFAULT, args: tuple | None = Values.DEFAULT) -> None:
        """Edit the Button item\n
        Parameters
        ----------
        * text: str (Facultative)\n
            The text of the button, if not specified, don't change
        * callback: FunctionType (Facultative)\n
            The function to callback when button is clicked, if None, don't callback, if not specified, don't change
        * args: tuple (Facultative)\n
            The arguments to pass to the callback, MUST be a tuple, if not specified, don't change"""

        # Set new values, if the value is Balues.DEFAUT, don't change
        if text is not Values.DEFAULT:
            self.text = text
    
        if callback is not Values.DEFAULT:
            self.callback = callback

        if args is not Values.DEFAULT:
            self.callback_args = args

        self.item = self.__create_item() # Create the new item
        self._update() # Trigger a menu update
        return

    def __callback(self, tray: Icon, item: pystray_MenuItem) -> None:
        """Manage the callback of the button"""
        if isinstance(self.callback, FunctionType): # Check if the callback is a function
            if isinstance(self.callback_args, tuple): # Check if the args is a tuple
                self.callback(*self.callback_args) # Call the callback with the given arguments

            else:
                self.callback() # Call the callback without arguments
        return

    def __create_item(self)  -> pystray_MenuItem:
        """Create the pystray_MenuItem Button object"""
        return pystray_MenuItem(self.text, self.__callback)



class CheckBox(Item):
    def __init__(self, text: str, check_default: bool | None = False, checked_callback: FunctionType | None = None, checked_callback_args: tuple | None = None, unchecked_callback: FunctionType | None = None, unchecked_callback_args: tuple | None = None) -> None:
        """Create a CheckBox item\n
        Parameters
        ----------
        * text: str\n
            The text of the checkbox
        * check_default: bool | None (Facultative)\n
            The status of the checkbox at start (checked (True) / not checked (False)) if None, the checkmark will not display
        * checked_callback: FunctionType (Facultative)\n
            The function to callback when the checkbox is clicked and switch from unchecked to checked
        * checked_callback_args: tuple (Facultative)\n
            The arguments to pass to the checked_callback, MUST be a tuple
        * unchecked_callback: FunctionType (Facultative)\n
            The functiion to callback when the checkbox is clicked and switch from checked to unchecked
        * unchecked_callback_args: tuple (Facultative)\n
            The arguments to pass to the unchecked_callback, MUST be a tuple"""


        self.tray: Optional[TrayManager] = None
        self.text = text

        self.checked_callback = checked_callback
        self.checked_callback_args = checked_callback_args
        self.unchecked_callback = unchecked_callback
        self.unchecked_callback_args = unchecked_callback_args

        if check_default == None:
            check_default = False
            disabled = True
        else:
            disabled = False

        self.status =  {"current": None, "requested": check_default, "disabled": disabled} # The dict we'll use to change the checkbox status (The checkmark state of our checkbox)
        self.item = self.__create_item()
        return

    def edit(self, text: str = Values.DEFAULT, check_default: bool | None = Values.DEFAULT, checked_callback: FunctionType | None = Values.DEFAULT, checked_callback_args: tuple | None = Values.DEFAULT, unchecked_callback: FunctionType | None = Values.DEFAULT, unchecked_callback_args: tuple | None = Values.DEFAULT) -> None:
        """Edit the CheckBox item\n
        Parameters
        ----------
        * text: str (Facultative)\n
            The text of the checkbox, if not specified, don't change
        * check_default: bool | None (Facultative)\n
            The status of the checkbox at start (checked (True) / not checked (False)) if None, the checkmark will not display, if not specified, don't change
        * checked_callback: FunctionType (Facultative)\n
            The function to callback when the checkbox is clicked and switch from unchecked to checked, if not specified, don't change
        * checked_callback_args: tuple (Facultative)\n
            The arguments to pass to the checked_callback, MUST be a tuple, if not specified, don't change
        * unchecked_callback: FunctionType (Facultative)\n
            The functiion to callback when the checkbox is clicked and switch from checked to unchecked, if not specified, don't change
        * unchecked_callback_args: tuple (Facultative)\n
            The arguments to pass to the unchecked_callback, MUST be a tuple, if not specified, don't change"""
        
        # Set new values, if the value is Balues.DEFAUT, don't change

        if text is not Values.DEFAULT:
            self.text = text

        if check_default is not Values.DEFAULT:
            if check_default == None:
                self.status["disabled"] = True
            else:
                self.status["disabled"] = False
                self.status["requested"] = check_default
        

        if checked_callback is not Values.DEFAULT:
            self.checked_callback = checked_callback
        
        if checked_callback_args is not Values.DEFAULT:
            self.checked_callback_args = checked_callback_args
        
        if unchecked_callback is not Values.DEFAULT:
            self.unchecked_callback = unchecked_callback
        
        if unchecked_callback_args is not Values.DEFAULT:
            self.unchecked_callback_args = unchecked_callback_args
            
        self.item = self.__create_item() # Create the new item
        self._update() # Trigger a menu update
        return

    def get_status(self) -> bool | None:
        """Return the current status of the checkbox (checked = True, unchecked = False, disabled = None)"""
        return self.status["current"]
    
    def set_status(self, new_status: bool | None) -> None:
        """Set the status of the checkbox\n
            Parameter
            ----------
            * new_status: bool | None\n
                The new status of the checkbox (checked = True, unchecked = False, disabled = Nonen)"""
        
        if new_status == None:
            self.status["disabled"] = True # Disable the checkbox update (The checkmark of the checkbox update)
        
        else:
            # Set the new value in the dict
            self.status["disabled"] = False
            self.status["requested"] = new_status

        self._update() # Trigger a menu update
        return

    def __callback(self, tray: Icon, item: pystray_MenuItem) -> None:
        """Manage the callback and the new status of the checkbox when clicked on in the menu and call callback, private function, do not use"""

        if self.status["disabled"]: # If the checkbox is disable don't do anything and return
            return
        
        self.status["current"] = not self.status["current"] # Change the status of the checkbox
        self._update() # Trigger a menu update
        
        if self.status["current"] == True:
            if isinstance(self.checked_callback, FunctionType): # Check if the checked_callback is a function
                if isinstance(self.checked_callback_args, tuple): # Check if the args is a tuple
                    self.checked_callback(*self.checked_callback_args) # Call the callback with the given arguments
                else:
                    self.checked_callback() # Call the callback without arguments

        elif self.status["current"] == False:
            if isinstance(self.unchecked_callback, FunctionType): # Check if the unchecked_callback is a function
                if isinstance(self.unchecked_callback_args, tuple): # Check if the args is a tuple
                    self.unchecked_callback(*self.unchecked_callback_args) # Call the callback with the given arguments
                else:
                    self.unchecked_callback() # Call the callback without arguments
        return

    def __update_status(self) -> bool:
        """Update the status of the checkbox"""
        if self.status["requested"] != None: # Check if a change a status was requested
            self.status["current"] = self.status["requested"] # Change the status
            self.status["requested"] = None # Set the request to None
        return self.status["current"] # Returns the current status
    
    def __create_item(self) -> pystray_MenuItem:
        """Create the pystray_MenuItem CheckBox object"""
        return pystray_MenuItem(self.text, self.__callback, lambda item: self.__update_status())



class Separator(Item):
    def __init__(self) -> None:
        """Create a Separator item"""

        self.item = pystray_Menu.SEPARATOR # Create the separator item
        self.tray: Optional[TrayManager] = None
        return



class Submenu(Item):
    def __init__(self, text: str) -> None:
        """Create a Submenu item\n
        Parameter
        ---------
        * text: str\n
            The text of the submenu"""

        self.items = []
        self.text = text
        self.tray: Optional[TrayManager] = None

        self.__default_item = Label("") # Set the default label to be added when the submenu doesn't contain any displayable item (such as Separators)
        return

    def edit(self, text: str) -> None:
        """Edit the Submenu item\n
        Parameter
        ---------
        * text: str\n
            The text of the submenu"""
        
        self.text = text
        self._update() # Trigger a menu update
        return
    
    def add(self, item: Union[Label, Button, CheckBox, Separator, 'Submenu'], index: int = -1) -> None:
        """Add an item to the submenu\n 
        Note: You can't add a submenu that contain the current submenu, this is prohibited as it would create a recursion loop\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to add to the submenu
        * index: int (Facultative)\n
            The index at which the item is going to be appened (Define the order of the items in the submenu)"""
        
        if isinstance(item, Submenu):
            if self.__check_recursion_loop(item): # Verify that their is no circular add
                raise CircularAddException(self, item)

        item.tray = self.tray
        
        # Add the item to the submenu
        if index == -1:
            self.items.append(item)
        else:
            self.items.insert(index, item)

        self._update() # Trigger a menu update
        return

    def remove(self, item: Union[Label, Button, CheckBox, Separator, 'Submenu']) -> Union[Label, Button, CheckBox, Separator, 'Submenu'] | None:
        """"Remove an item from the submenu\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to remove from the submenu"""
        
        try: 
            index = self.items.index(item) # Try to get the item index
        except ValueError:
            return
    
        removed = self.items.pop(index) # Remove the item
        self._update() # Trigger a menu update
        return removed # Return the removed item
    
    def get_items(self) -> list[Union[Label, Button, CheckBox, Separator, 'Submenu']]:
        """Return the items contained in the submenu"""
        return self.items
    
    def __check_recursion_loop(self, submenu: 'Submenu') -> bool:
        """Check if the submenu is not in the given submenu (Used to detect recursion loop)"""
        for item in submenu.get_items():
            if item == self: # Check if the item is the same self
                return True
            
            if isinstance(item, Submenu):
                if self.__check_recursion_loop(item): # Check recursively if the submenu is in the added submenu
                    return True
        return False
    
    def _create_submenu(self) -> pystray_MenuItem:
        """Create the pystray_MenuItem Submenu object"""
        items: list[Label | Button | CheckBox | Separator | Submenu] = []

        for item in self.items:
            if isinstance(item, Submenu): 
                item.tray = self.tray
                item = item._create_submenu() # Create the pystray_MenuItem of that submenu

            elif isinstance(item, Label) or isinstance(item, Button) or isinstance(item, CheckBox) or isinstance(item, Separator):
                item.tray = self.tray
                item = item.item # Get the pystray_MenuItem of the item
            
            items.append(item)
        
        if len(items) == 0 or all(isinstance(i, Separator) for i in self.items): # Check if the submenu is empty or if all the items in the submenu are not displayable without other items (Such as Separators)
            items.append(self.__default_item.item) # Add the default item to allow the submenu to be displayed
        return pystray_MenuItem(self.text, pystray_Menu(*items))



class Menu:
    def __init__(self, tray: 'TrayManager') -> None:
        """Create the menu in the notification tray (Automatically created when you create a TrayManager object)"""

        self.tray = tray
        self.items: list[Label | Button | CheckBox | Separator | Submenu] = []
        self._default_item = Label("") # Set the default label to be added when the menu doesn't contain any displayable item (such as Separators)
        return

    def add(self, item: Label | Button | CheckBox | Separator | Submenu, index: int = -1) -> None:
        """Add an item to the menu\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to add to the menu
        * index: int (Facultative)\n
            The index at which the item is going to be appened (Define the order of the items in the menu)"""
        
        item.tray = self.tray

        # Add the item to the menu
        if index == -1:
            self.items.append(item)
        else:
            self.items.insert(index, item)

        self.update() # Trigger a menu update
        return
    
    def remove(self, item: Label | Button | CheckBox | Separator | Submenu) -> Label | Button | CheckBox | Separator | Submenu | None:
        """Remove an item from the menu\n
        Parameters
        ----------
        * item: Label | Button | CheckBox | Separator | Submenu\n
            The item to remove from the menu"""
        
        try:
            index = self.items.index(item) # Try to get the item index
        except ValueError:
            return

        removed = self.items.pop(index) # Remove the item
        self.update() # Trigger a menu update
        return removed # Return the removed item

    def get_items(self) -> list[Label | Button | CheckBox | Separator | Submenu]:
        """Return the items contained in the menu"""
        return self.items
    
    def update(self) -> None:
        """Update the menu"""
        self.tray.tray.update_menu()
        return

    def _create_menu(self) -> list[pystray_MenuItem]:
        """Create the list of items composing the menu"""
        items: list[Label | Button | CheckBox | Separator | Submenu] = []

        for item in self.items:
            if isinstance(item, Submenu):
                item.tray = self.tray
                item = item._create_submenu() # Create the pystray_MenuItem of that submenu
    
            elif isinstance(item, Label) or isinstance(item, Button) or isinstance(item, CheckBox) or isinstance(item, Separator):
                item.tray = self.tray
                item = item.item # Get the pystray_MenuItem of the item

            items.append(item)
        
        if len(items) == 0 or all(isinstance(i, Separator) for i in self.items): # Check if the menu is empty or if all the items in the menu are not displayable without other items (Such as Separators)
            items.append(self._default_item.item) # Add the default item to allow the menu to be displayed
        return items



class TrayManager:
    def __init__(self, app_name: str, icon: Image.Image | bytes | str | None = None, default_show: bool = False, run_in_main_thread: bool = False) -> None:
        """Create a pystray.Icon object linked to a Menu() object\n
            Parameters
            ----------
            * app_name: str\n
                The name of the app in the notification tray
            * icon: Image.Image | bytes | str (Facultative)\n
                The image to use as the icon for your app in the notification tray, if not provided or if the app is unable to open load the image, use a white square
            * default_show: bool (Facultative)\n
                Define if the icon is displayed in the notifaction tray when you create your TrayManager object
            * run_in_main_thread: bool (Facultative)\n
                If set on True, run the pystray loop in the main thread, recommended by pystray's docs for compatibility, else run the pystray loop in a new thread"""


        self.menu = Menu(self) # Create the menu item
        self.default_icon = Image.new("L", (32, 32), 255) # Create the default icon

        # Set the icon of the app in the notification tray
        if icon:
            if isinstance(icon, Image.Image):
                self.icon = icon
            else:
                self.icon = Image.open(icon)
        else:
            self.icon = self.default_icon

        # Create the pystray_Icon object
        self.tray = pystray_Icon(app_name, self.icon, title=app_name, menu=pystray_Menu(lambda: self.menu._create_menu())) # Here we use lamda to allow the menu to dynamically update
        

        if run_in_main_thread:
            self.__run(default_show) # Run the pystray loop in the main thread
        
        else:
            #Run it in different thread (pystray.Icon.run() is a blocking function)
            thread = Thread(target=self.__run, args=(default_show,))
            thread.start()
        return

    def set_app_name(self, name: str) -> None:
        """Set the name of the app in the notification tray"""
        self.tray.title = name
        return

    def set_icon(self, icon: Image.Image | bytes | str | None, show: bool = True) -> None:
        """Set icon of app in the notification tray\n
            Parameters
            ----------
            * icon: Image.Image | bytes | str | None\n
                The image to use as the icon for your app in the notification tray, if None or if the app is unable to open load the image, use a white square
            * show: bool (Facultative)\n
                Define if the icon should be displayed in the notification tray if it was previously hidden"""

        # Set the icon of the app in the notification tray
        if icon:
            if isinstance(icon, Image.Image):
                self.icon = icon
            else:
                self.icon = Image.open(icon)
        else:
            self.icon = self.default_icon

        self.tray.icon = self.icon

        if show: # Show the icon in the notification tray
            self.show()
        return

    def show(self) -> None:
        """Show the icon in the notification tray"""
        # Show the icon in the notification tray
        self.tray.visible = True
        return
    
    def hide(self) -> None:
        """Hide the icon in the notification tray"""
        # Hide the icon in the notification tray
        self.tray.visible = False
        return

    def kill(self) -> list[Label | Button | CheckBox | Separator | Submenu]:
        """Kill the pystray_Icon, return the items of the menu as list"""
        
        items = self.menu.get_items() # Get the items of the menu
        self.tray.stop() # Stop the pystray_Icon loop
        return items # Return the items

    def __run(self, default_show: bool) -> None:
        """Run the pystray_Icon object"""
        if default_show == False:
            # We use lamda _: To avoid the problems related to the number of arguments
            callback = lambda _: self.hide()

            # Run pystray_Icon loop and callback to hide the icon at start
            self.tray.run(callback)
        else:
            self.tray.run() # Run the pystray_Icon loop
        return