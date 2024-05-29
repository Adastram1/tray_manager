# What is tray_manager ?
TrayManager is a package for adding a system tray icon, based on pystray (https://github.com/moses-palmer/pystray by Moses Palmér), this package is an "easier" version of pystray to manipulate based on the use of object (Object Oriented Programming).

# How do I install it ?
tray_manager is publisehd on PyPi (https://pypi.org/project/tray-manager/) and can be downloaded by using :
```shell
pip install tray-manager
```

# Usage
1. [Create and use a TrayManager object](https://github.com/Adastram1/tray_manager/blob/main/README.md#create-and-use-a-traymanager-object)
2. [Create and interact with Items](https://github.com/Adastram1/tray_manager/blob/main/README.md#create-and-interact-with-items)
3. [Add items to the Menu](https://github.com/Adastram1/tray_manager/blob/main/README.md#add-the-items-to-the-menu)
4. [Customize the TrayManager object](https://github.com/Adastram1/tray_manager/blob/main/README.md#customize-the-traymanager-object)
5. [Customize and edit the items](https://github.com/Adastram1/tray_manager/blob/main/README.md#customize-and-edit-the-items)
6. [Check for OS supported features](https://github.com/Adastram1/tray_manager/blob/main/README.md#check-for-os-supported-features)
7. [Notifications](https://github.com/Adastram1/tray_manager/blob/main/README.md#notifications-currently-unavaible) [CURRENTLY UNAVAIBLE]
8. [Advanced settings](https://github.com/Adastram1/tray_manager/blob/main/README.md#advanced-settings)
9. [Examples](https://github.com/Adastram1/tray_manager/blob/main/README.md#examples)

## Create and use a TrayManager Object
The main object of the librairy is the TrayManager object, it is the central element and can be considered as the icon in the system tray itself, it contains all the elements of our app.

To create one, you need to import the tray_manager.TrayManager class and create a tray object as followed :
```python
from tray_manager import TrayManager
my_tray = TrayManager(app_name="My App")
```

To stop the app, you need to use the .kill() function (Note : The .kill() function returns all the items that were contained in the menu object) as followed (Note : The Menu and TrayManager objetcts become useless)

```python
from tray_manager import TrayManager, Label, Button

my_tray = TrayManager("My App", run_in_seperate_thread=True)
my_menu = my_tray.menu

def my_callback():
  print("Hello")

my_label = Label("My Label")
my_button = Button("My Button", my_callback)

my_menu.add(my_label)
my_menu.add(my_button)

my_tray.kill()
-> [my_label, my_button]
```

## Create and interact with Items
The items are the elements of your app, they will be displayed in the menu they're added to. Their is different kinds of items that all works in a similar way but each have some specificities. 

Here is the list of all the items :
1. [Label](https://github.com/Adastram1/tray_manager/blob/main/README.md#label)
2. [Button](https://github.com/Adastram1/tray_manager/blob/main/README.md#button)
3. [CheckBox](https://github.com/Adastram1/tray_manager/blob/main/README.md#checkbox)
4. [Separator](https://github.com/Adastram1/tray_manager/blob/main/README.md#separator)
5. [Submenu](https://github.com/Adastram1/tray_manager/blob/main/README.md#submenu)

### Label
The label is the most basic item, it is only constituated of a text.

To create one, you need to use the tray_manager.Label class as followed :

```python
from tray_manager import Label
my_label = Label("My Label")
```



### Button
The button is like the label item but you can add a callback argument (FunctionType) that will be called when the user clicks on the button. You can also specify some arguments as a tuple that will be passed too your function when the callback runs.

To create one, you need to use the tray_manager.Button class as followed : 

```python
from tray_manager import Button
def my_callback(text: str) -> None:
  print(text)

my_button = Button("My Button", my_callback, args=("Hello",))
```


### CheckBox
The CheckBox item is a bit more complex than a regular button, it has 2 differents callbacks instead of 1 and different arguments for each, one for when the checkbox switch from the 'Disabled' to 'Enabled' state (Not checked to checked), and one for when it switch from the 'Enabled' to 'Disabled' state (Checked to not checked).

You can 'Disable' the interactions with your checkbox by setting the value of check_default to None (Note : The callback won't be called if the user clicks on the checkbox when it is disabled).

To create one, you need to use the tray_manager.CheckBox class as followed :

```python
from tray_manager import CheckBox

def checked(text: str) -> None:
  print(f"In procedure 'checked' : {text}")

def unchecked(text: str) -> None:
  print(f"In procedure 'unchecked' : {text}")

my_checkbox = CheckBox("My CheckBox", check_default=False, checked_callback=checked, checked_callback_args=("I'm now checked",),
                        unchecked_callback=unchecked, unchecked_callback_args=("I'm now unchecked",))
```

To get the current state of the checkbox (checked : True | unchecked : False | disabled : None), you can use the .get_status() function as followed :

```python
from tray_manager import CheckBox

my_checkbox = CheckBox("My CheckBox")

my_checkbox.get_status()
-> bool | None
```

You can also set the state of the checkbox by using the .set_status() function as followed : 

```python
from tray_manager import CheckBox

my_checkbox = CheckBox("My CheckBox")

my_checkbox.set_status(True)
-> Checked
my_checkbox.set_status(False)
-> Unchecked
my_checkbox.set_status(None)
-> Disabled
```



### Separator
The separator is a built-in object of Pystray, it doesn't require any parameters.

To create one, you need to use the tray_manager.Separator class as followed : 

```python
from tray_manager import Separator
my_separator = Separator()
```



### Submenu
The submenu is like a Menu() object and can contains other items including other submenu. Be carreful when adding submenu into each others as adding a submenu to itself will generate an tray_manager.CircularAddException error.

To create one, you need to use the tray_manager.Submenu as followed : 

```python
from tray_manager import Submenu
my_submenu = Submenu("My Submenu")
```

To add an item to the submenu, you can use the .add() function as followed : 

```python
from tray_manager import Submenu, Label
my_submenu = Submenu("My Submenu")
my_label = Label("My Label")

my_submenu.add(my_label)
```
To remove an item from the submenu, you can use the .remove() function as followed : (Note : The .remove() function returns the item that was removed) 

```python
from tray_manager import Submenu, Label
my_submenu = Submenu("My Submenu")
my_label = Label("My Label")

my_submenu.add(my_label)

my_submenu.remove(my_label)
-> my_label
```


To get the items contained in a submenu, you can use the .get_items() function as followed:

```python
from tray_manager import Submenu, Label, Button

def my_callback()
  print("Hello")

my_submenu = Submenu("My Submenu")
my_label = Label("My Label")
my_button = Button("My Button", my_callback)

my_submenu.add(my_label)
my_submenu.add(my_button)

my_submenu.get_items()
-> [my_label, my_button]
```

## Add the items to the Menu
Check tray_manager.OsSupport.HAS_MENU for disponibility on your OS. The menu is one of the central elements of this library, it works like a submenu but cannot be removed from the TrayManager object.

It is created automatically when you create a TrayManager object if your OS support the menu. To acces it, you need to acces the TrayManager.menu object as followed : 
```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)
my_menu = my_tray.menu
```

To add an item to the menu, you can use the .add() function as followed : 

```python
from tray_manager import TrayManager, Label
my_tray = TrayManager("My App", run_in_seperate_thread=True)
my_menu = my_tray.menu

my_label = Label("My Label")

my_menu.add(my_label)
```
To remove an item from the menu, you can use the .remove() function as followed : (Note : The .remove() function returns the item that was removed) 

```python
from tray_manager import TrayManager, Label
my_tray = TrayManager("My App", run_in_seperate_thread=True)
my_menu = my_tray.menu

my_label = Label("My Label")
my_menu.add(my_label)

my_menu.remove(my_label)
-> my_label
```


To get the items contained in a menu, you can use the .get_items() function as followed:

```python
from tray_manager import TrayManager, Menu, Label, Button

def my_callback()
  print("Hello")

my_tray = TrayManager("My App", run_in_seperate_thread=True)
my_menu = my_tray.menu

my_label = Label("My Label")
my_button = Button("My Button", my_callback)

my_menu.add(my_label)
my_menu.add(my_button)

my_menu.get_items()
-> [my_label, my_button]
```

To update the menu display, you can use the function .update(). It is normally triggered every time you edit an item or the menu.
```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)
my_menu = my_tray.menu

my_menu.update()
```

## Customize the TrayManager object
You can customize your TrayManager object in different ways such as :

1. [Setting a new name for the app](https://github.com/Adastram1/tray_manager/blob/main/README.md#setting-a-new-name-for-the-app)
2. [Setting a new icon for the app](https://github.com/Adastram1/tray_manager/blob/main/README.md#setting-a-new-icon-for-the-app)
3. [Hiding / Showing the app in the system tray](https://github.com/Adastram1/tray_manager/blob/main/README.md#hiding--showing-the-app-in-the-system-tray)

### Setting a new name for the app
To set a new name for your app you can use the .set_app_name() function of the tray_manager.TrayManager object as followed :
```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)

my_tray.set_app_name("My new App")
```
### Setting a new icon for the app
tray_manager use a memory load system for icons, to set a new icon for your app, you first need to load it using the .load_icon(), then set the icon as the new icon using the .set_icon() functions of the tray_manager.TrayManager object.

By default, the icon is a white square of 32x32 pixels. The default icon is always loaded in memory and can be set by passing the argument tray_manager.Values.DEFAULT to the .set_icon() function.

To load an icon, you need to use the .load_icon() function of the tray_manager.TrayManager object and pass it an file path, a encoded image, a PIL.Image object or any file that can be read and interpreted as an image by PIL. You also need to pass a name that will be used as a key in the icons dictionnary to retreive your icon.

```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)

my_tray.load_icon("my_icon_file_path.png", "my_new_icon")
```

To set an icon, you need to use the .set_icon() function of the tray_manager.TrayManager object and pass it the name (key) of your icon that you set when using .load_icon().

```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)

my_tray.load_icon("my_icon_file_path.png", "my_new_icon")
my_tray.set_icon("my_new_icon")
```

### Hiding / Showing the app in the system tray
Instead of killing the tray_manager.TrayManager object when you want it to stop being displayed in the system tray and creating a new one once you need it again, you can use the .show() and .hide() functions of the the tray_manager.TrayManager object to control whether the app is visible in the system tray or not. You can specify the default_show argument of the tray_manager.TrayManager object when creating it to define whether it will be displayed or not once the object is created.

To show the app in the system tray, you can use the .show() function of the the tray_manager.TrayManager object as followed : 
```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)

my_tray.show()
```

To hide the app in the system tray, you can use the .hide() function of the the tray_manager.TrayManager object as followed :
```python
from tray_manager import TrayManager
my_tray = TrayManager("My App", run_in_seperate_thread=True)

my_tray.hide()
```

## Customize and edit the items
To edit an already created item, you can use the .edit() function of the item, when doing so, you only need to specify which arguments you want to change, and the others will stay the same as they were.

To edit an item you can do as followed : 
```python
from tray_manager import Button

def my_first_callback():
  print("Hello")
  my_button.edit(callback=my_second_callback)

def my_second_callback():
  print("World !")

my_button = Button("My Button", my_first_callback)

# When clicking on the button, this will display :
# First click
-> Hello
# Second click
-> World !
```
You can custom the items in different ways such as : 

1. [Enabling / Disabling the item (Gray look and stop interactions)](https://github.com/Adastram1/tray_manager/blob/main/README.md#enabling--disabling-the-item-gray-look-and-non--responsive)
2. [Setting the default attribut to the item (Bold look)](https://github.com/Adastram1/tray_manager/blob/main/README.md#setting-the-default-attribut-to-the-item-bold-look)
3. [Setting the radio look on the checkbox (A dot instead of a crossmark)](https://github.com/Adastram1/tray_manager/blob/main/README.md#setting-the-radio-look-on-the-checkbox-a-dot-instead-of-a-crossmark)

### Enabling / Disabling the item (Gray look and non-responsive)
If you want to display the item but you want it to be non-responsive (for Button, CheckBox and Submenu) and look like a disabled item, you can use the .enable() and .disable() functions of the item. By default, every items are enabled. Note : every item can be disabled except for the separator.

To enable your item, you can, use the .enable() function of the item as followed : 
```python
from tray_manager import CheckBox

def checked_callback():
  print("Checked")

def unchecked_callback():
  print("Unchecked")

my_checkbox = CheckBox("My CheckBox", checked_callback=checked_callback, unchecked_callback=unchecked_callback)

my_checkbox.enable()
```

To disable your item, you can, use the .disable() function of the item as followed : 
```python
from tray_manager import CheckBox

def checked_callback():
  print("Checked")

def unchecked_callback():
  print("Unchecked")

my_checkbox = CheckBox("My CheckBox", checked_callback=checked_callback, unchecked_callback=unchecked_callback)

my_checkbox.disable()
```

### Setting the default attribut to the item (Bold look)
To make your item the default of the menu / submenu and give it a bold look, you can set the default attribut when creating / editing the item. You can only have 1 default item by menu / submenu. By default, there is no default item.

To set the default attribut of the item, you can do as followed : 

When creating the item : 
```python
from tray_manager import Label
my_label = Label("My Label", default=True)
```

When editing the item : 
```python
from tray_manager import Label
my_label = Label("My Label")
my_label.edit(default=True)
```

### Setting the radio look on the checkbox (A dot instead of a crossmark)
If you want to give a new look to your regular checkbox crossmark, you can use the use_radio_look attribut of the CheckBox when creating / editing the CheckBox.

To set the use_radio_look attribut of the item, you can do as followed : 

When creating the item : 
```python
from tray_manager import CheckBox

def checked_callback():
  print("Checked")

def unchecked_callback():
  print("Unchecked")

my_checkbox = CheckBox("My CheckBox", checked_callback=checked_callback, unchecked_callback=unchecked_callback, use_radio_look=True)
```

When editing the item : 
```python
from tray_manager import CheckBox

def checked_callback():
  print("Checked")

def unchecked_callback():
  print("Unchecked")

my_checkbox = CheckBox("My CheckBox", checked_callback=checked_callback, unchecked_callback=unchecked_callback)
my_checkbox.edit(use_radio_look=True)
```

## Check for OS supported features

## Notifications [CURRENTLY UNAVAIBLE]

## Advanced settings

## Examples
