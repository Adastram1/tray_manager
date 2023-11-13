import os
from pystray import Icon as pystray_Icon, Menu as pystray_Menu, MenuItem as pystray_MenuItem
from PIL import Image
import threading
from plyer import notification as plyer_notification
import tkinter as tk
import time
from enum import Enum
import types
from functools import partial


Lang = {"Test1": "Test", "Test2": "Test2", "Test3": "Test3"}




class Menu():
    class Default(Enum):
        DEFAULT = "DefaultValue"


    class ItemType(Enum):
        LABEL = "LabelType"
        BUTTON = "ButtonType"
        CHECK = "CheckType"
        SUBMENU = "SubmenuType"
        SEPARATOR = "SeparatorType"


    def __init__(self):
        """Create a pystray.MenuItem \n
            Used to set the options of the app in the notification tray"""

        self.id = 0
        self.ItemsFromID = {} # id: pystray.MenuItem, (DicKey, callback, item_type, {"current": bool | None, "requested": bool | None}, index)
        self.IDsFromItem = {} # pystray.MenuItem: id



    def create_item(self, DicKey: str = "TEST", callback: types.FunctionType | None = None, item_type: ItemType = ItemType.LABEL, checkdefault: bool = False, index: int | None = None, FORCE_ID: int | None = None):
        """Create an item that will be displayed in the options of the app notification in the notification tray\n
            Parameters
            ----------
            * DicKey\n
            The key of the word you want to display from the Lang dict
            * callback (Facultative)\n
            The function to callback after the button is clicked
            * item_type (Facultative)\n
            The type of the item to create (see Menu.ItemType)
            * checkdefault (Facultative)\n
            Only use with item_type as Menu.ItemType.CHECK, define the default status of the item, True = checked, False = not checked
            * index (Facultative)\n
            The place of the item when it display, if None add at the end, if conflict, first added will use the correct index, followed by the ones in conflict
            
            Returns
            -------
            * Item ID\n
            The ID of the item, used to remove it with delete_item"""

        #Check item type
        if item_type == self.ItemType.LABEL:
            #Reserve id
            if FORCE_ID:
                id = FORCE_ID

            else:
                self.id += 1
                id = self.id


            #Create item and add it to lists
            self.ItemsFromID[id] = (pystray_MenuItem(Lang.get(DicKey, "UNDEFINED"), lambda icon, item: None), (DicKey, callback, item_type, {"current": None, "requested": checkdefault}, index))
            self.IDsFromItem[self.ItemsFromID[id][0]] = id

            return id


        elif item_type == self.ItemType.BUTTON:
            #Check if callback is a callable object
            if callable(callback):
                #Reserve id
                if FORCE_ID:
                    id = FORCE_ID

                else:
                    self.id += 1
                    id = self.id

                #Use partial to pass our arguments to our callback
                menu_callback = partial(self.__menu_callback, id, callback)

                #Create item and add it to lists
                self.ItemsFromID[id] = (pystray_MenuItem(Lang.get(DicKey, "UNDEFINED"), menu_callback), (DicKey, callback, item_type, {"current": None, "requested": checkdefault}, index))
                self.IDsFromItem[self.ItemsFromID[id][0]] = id
                return id

            else:
                raise ValueError("callback is not callable")


        elif item_type == self.ItemType.CHECK:
            #Check if callback is a callable object
            if callable(callback):
                #Reserve id
                if FORCE_ID:
                    id = FORCE_ID

                else:
                    self.id += 1
                    id = self.id

                #Use partial to pass our arguments to our callback
                menu_callback = partial(self.__menu_callback, id, callback)

                #Create item and add it to lists
                self.ItemsFromID[id] = (pystray_MenuItem(Lang.get(DicKey, "UNDEFINED"), menu_callback, checked=lambda item: self.__change_status(item)), (DicKey, callback, item_type, {"current": None, "requested": checkdefault}, index))
                self.IDsFromItem[self.ItemsFromID[id][0]] = id
                return id

            else:
                raise ValueError("callback isn't callable ! Please link callback to a function")



        elif item_type == self.ItemType.SUBMENU:
            raise NotImplementedError
        


        elif item_type == self.ItemType.SEPARATOR:
            #Reserve id
            if FORCE_ID:
                id = FORCE_ID

            else:
                self.id += 1
                id = self.id

            self.ItemsFromID[id] = (pystray_Menu.SEPARATOR, (None, None, None, None, index))
            self.IDsFromItem[self.ItemsFromID[id][0]] = id
            return id

        else:
            #Unknow item
            raise ValueError("Unknow ItemType")
            


    def delete_item(self, item_id: int):
        #Check if item exist
        if item_id in self.ItemsFromID:

            #Remove item from list
            self.IDsFromItem.pop(self.ItemsFromID[item_id][0])
            item = self.ItemsFromID.pop(item_id)

            #Return Item and parameters (Used by edit_item and if user wants to get the parameters back)
            return item
        
        else:
            raise IndexError("Item doesn't exist")



    def edit_item(self, item_id: int, DicKey: str | Default = Default.DEFAULT, callback: types.FunctionType | None | Default = Default.DEFAULT, item_type: ItemType | Default = Default.DEFAULT, checkdefault: bool | Default = Default.DEFAULT, index: int | None | Default = Default.DEFAULT):
        """Combination of delete_item() and create_item() Note: Does not change the id of the item\n
            Parameters
            ----------
            * item_id (Required)\n
            The id of the item you want to edit
            * DicKey (Facultative)\n
            The key of the word you want to display from the Lang dict, if Default.DEFAULT don't change value
            * callback (Facultative)\n
            The function to callback after the button is clicked, if None, don't link to a callback, if Default.DEFAULT, don't change value
            * item_type (Facultative)\n
            The type of the item to create (see Menu.ItemType), if Default.DEFAULT don't change value
            * checkdefault (Facultative)\n
            Only use with item_type as ItemType.CHECK, define the default status of the item, True = checked, False = not checked, if Default.DEFAULT don't change value
            * index (Facultative)\n
            The place of the item when it display, if  add at the end, if conflict, first added will use the correct index, followed by the ones in conflict, if Default.DEFAULT don't change value
            * FORCE_ID (Usage not recommended)\n
            Force the item to use a specific id. WARNING MIGHT OVERWRITE EXISTING ITEMS IF NOT DELETED CORRECTLY
            """
        
        #Delete item and get the parameters
        item = self.delete_item(item_id)
        
        #For every test : if new value = Default.DEFAULT, use previous one
        if DicKey == self.Default.DEFAULT:
            DicKey = item[1][0]

        if callback == self.Default.DEFAULT:
            callback = item[1][1]

        if item_type == self.Default.DEFAULT:
            item_type = item[1][2]

        if checkdefault == self.Default.DEFAULT:
            checkdefault = item[1][3]

        if index == self.Default.DEFAULT:
            index = item[1][4]
        
        #Return function
        return self.create_item(DicKey, callback, item_type, checkdefault, index, FORCE_ID=item_id)

            

    def get_items(self, get_parameters : bool = False):
        """Get all the items in the dict of items and return them as a list of pystray.Menu objects\n
            Parameter
            ---------
            * get_parameters (Facultative)\n
            Return the items and parameters as a list of tuples"""

        NonIndexedItems = []
        NonIndexedTuples = []
        IndexedItems = []

        #Get all ids in the dic
        for key in self.ItemsFromID.keys():

            #Check for index key
            
            if self.ItemsFromID[key][1][4] == None:
                #Sort items that don't have a specified value for index
                if get_parameters:
                    #Add both item and parameters
                    NonIndexedItems.append(self.ItemsFromID[key])
                else:
                    #Add only items
                    NonIndexedItems.append(self.ItemsFromID[key][0])
            else:
                #Sort items that have a specified value for index
                NonIndexedTuples.append(self.ItemsFromID[key])
        
        IndexedTuples = sorted(NonIndexedTuples, key= lambda x: x[1][4])

        #Add indexed tuples to the list
        for Item in IndexedTuples:
            if get_parameters:
                #Add both item and parameters
                IndexedItems.append(Item)
            else:
                #Add only item
                IndexedItems.append(Item[0])

        #Add non-indexed tuple to the end of the list
        for Item in NonIndexedItems:
            IndexedItems.append(Item)

        return IndexedItems



    def set_status(self, item_id: int, new_value: bool| None):
        """Set a check box status manually\n
            Parameters
            ----------
            * item_id (Requiered)
            The id of the item you want to edit
            * new_value (Requiered)\n
            The value to set for the item (True: Checked, False: Not Checked, None: Disabled)"""
        
        #Check if item is in list
        if item_id in self.ItemsFromID:
            #Check if item is a checkable object
            if self.ItemsFromID[item_id][1][2] == self.ItemType.CHECK:
                #Set new value
                self.ItemsFromID[item_id][1][3]["requested"] = new_value
                return True
            else:
                raise ValueError("Item doesn't have check attribute")
            
        raise ValueError("Item doesn't exist")
    


    def __change_status(self, item: pystray_MenuItem):
        """Private function DO NOT USE"""

        #Get dic
        CheckStatusDic = self.ItemsFromID[self.IDsFromItem[item]][1][3]

        #Get requested status
        Requested = CheckStatusDic["requested"]

        #If requestedd is None, it means it've been trigerred by a menu update, don't change anything
        if Requested == None:
            return CheckStatusDic["current"]
        
        #Set new value and set requested to None
        elif Requested == True:
            CheckStatusDic["current"] = True
            CheckStatusDic["requested"] = None
            return True
        
        #Set new value and set requested to None
        elif Requested == False:
            CheckStatusDic["current"] = False
            CheckStatusDic["requested"] = None
            return False
        
        else:
            raise ValueError("Invalid value requested")



    def __menu_callback(self, item_id: int, callback: types.FunctionType, tray: pystray_Icon, item: pystray_MenuItem):
        """Private function DO NOT USE"""
        
        #if item is checkable, update it's stauts
        if item.checked != None:
            self.ItemsFromID[item_id][1][3]["requested"] = not item.checked
        
        #Call the callback functionk
        callback()
    




class TrayManager():
    def __init__(self, Menu: Menu, AppName: str = "Test App", ImagePath: str | None = None, Icon: Image.Image | None = None, Lang: str = "en", default_show: bool = False):
        """Create a pystray.Icon object linked to a Menu() object\n
            Parameters
            ----------
            * Menu (Required)\n
            Menu() instance
            * AppName (Facultative)\n
            AppName is the name of your app in the notification tray (default = "Test App")
            * Path or Icon or Index (Facultative)\n
            Import the image from one of those 3 ways :\n
            Using ImagePath, ImagePath is the image path to use as icon (str)\n
            Using Icon, Icon is the PIL.Image.Image object\n
            Note : Your first image imported is the index 1 NOT 0\n
            If None is provided, use 'default' icon (white square of 32*32) which IS ALWAYS index 0"""

        #Self object :
        #self.Menu Menu() object
        #self.Icons List of PIL.Image.Image objects, first one is a white square of 32*32
        #self.tray pystray.Icon() object

        self.Menu = Menu
        

        default_image = Image.new("L", (32, 32), 255)
        self.Icons = [default_image]
        
        

        #Set the icon of the app in the notification tray
        if ImagePath: 
            if os.path.exists(ImagePath):
                #Open image as PIL.Image.Image object and add it to Icons list
                image = Image.open(ImagePath)
                self.Icons.append(image)
            else:
                raise FileNotFoundError(f"Can't find image at : '{ImagePath}'")

        elif Icon is Image.Image:
            #Add image to Icons list
            self.Icons.append(Icon)


        #Create pystray_Icon object
        self.tray = pystray_Icon(AppName, self.Icons[-1], title=AppName, menu=pystray_Menu(lambda: self.Menu.get_items()))
        

        #Run it in different thread (pystray.Icon.run() is a blocking function)
        Thread = threading.Thread(target=self.__run, args=(default_show,))
        Thread.start()



    def set_name(self, name: str):
        self.tray.title = name



    def set_icon(self, ImagePath: str | None = None, Icon: Image.Image | None = None, Index: int | None = None, Show: bool = True):
        """Set icon of app in the notification tray\n
            Parameters
            ----------
            * Self (Requiered)\n
            pystray.Icon object
            * Path or Icon or Index (Only one Requiered)\n
            Import the image from one of those 3 ways :\n
            Using ImagePath, ImagePath is the image path to use as icon (str)\n
            Using Icon, Icon is the PIL.Image.Image object\n
            Using Index, Index is the custom key of one of the previous imported images (Note : the 'default' key is a white square of 32*32)\n
            If None is provided, don't change anything and retutn False\n
            * Show (Facultative)\n
            Define if whether the icon should be displayed in the notification tray if .hide() was called before (Simillar as .show())\n
            Return
            -------
            False | Index of loaded Image
            """

        print(self.Icons)
        #Check if IconPath exist
        if ImagePath: 
            if os.path.exists(ImagePath):
                #Open image as PIL.Image.Image object and add it to Icons list

                image = Image.open(ImagePath)
                self.Icons.append(image)
                Index = len(self.Icons) - 1
            else:
                raise FileNotFoundError(f"Can't find image at : '{ImagePath}'")


        elif Image.isImageType(Icon):
            #Add image to Icons list
            image = Icon
            self.Icons.append(image)
            Index = len(self.Icons) - 1
        

        elif Index != None:
            if len(self.Icons) - 1 >= Index:
                image = self.Icons[Index]
            else:
                raise IndexError("Index of icons out of range")
            
        else:
            return False
        
        #Set image as icon 
        self.tray.icon = image

        if Show:
            #Call Tray.Show() to be sure only .Show() and .Hide() have control over whether the icon is visible or not
            self.show()

        return Index



    def delete_icon(self, Index: int, All: bool = False):
        """Remove the icon of Index or All the icons (Except the default one) from memory\n
            Parameters
            ----------
            * Index\n
            The index of the icon to remove from memory
            * All\n
            If True, remove all icons except the default one from memory\n
            Return
            ------
            PIL.Image.Image object of icon removed, if All = True, return list of PIL.Image.Image object of icons removed"""

        if All:
            Images = []
            
            #Append all images to list
            for x in self.Icons[1:-1]:
                Images.append(self.Icons.pop(x))

            return Images
        
        #If Index is correct, return value
        if len(self.Icons) - 1 >= Index and Index != 0:
            return self.Icons.pop(Index)
        
        else:
            raise IndexError("Index of icon out of range")



    def show(self, IconPath: str = None):
        """Show the icon in the notification tray, if icon is already displayed, don't change anything\n

            Parameters
            ----------
            * Self (Requiered)\n
            pystray.Icon object
            * IconPath (Facultatives)\n
            IconPath is the path of the image you want to use as the icon of your app in the notification tray, if not foud, raise FileNotFoundError
            """
        
        if IconPath:
            #Use Tray.SetIcon to set the icon
            self.set_icon(IconPath)
        
        #Set status to visible
        self.tray.visible = True
        return
    


    def hide(self):
        """Hide the icon in the notification tray, if icon is already hidden, don't have an effect"""

        #Set status to visible
        self.tray.visible = False
        return



    def kill(self):
        """Kill the app notification in notification tray and all the menu items, returns them as list of tuple (item, parameters)\n
            Note : TrayManager() and Menu() objetcs become useless"""
        
        #Stop the tray process and kill every menu instances, returns them as list of tuple
        Items = self.Menu.get_items(get_parameters=True)
        self.tray.stop()
        return Items



    def __run(self, default_show):
        if default_show == False:
            #Use lamda _: To avoid the problem related to the number of arguments
            callback = lambda _: self.hide()

            #Run pystray.Icon object with callback
            self.tray.run(callback)

        else:
            self.tray.run()

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    tray = TrayManager()