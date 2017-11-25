"""
File for the item class.
"""
from typing import Optional


class Items:
    """The Library of all items that currently exist.

    Contains all our items, names for items should be unique at all times.

    Dict contains name (str) and Value (float) pairs.
    """
    def __init__(self) -> None:
        self.library = dict()
        self.save_location = ''
        return

    def new_item(self, name: str, value: float = -1) -> bool:
        """Add an item to the library.

        :param name: Name of the item, must be unique.
        :param value: Value of the item. -1 means it has not been valued.
                      -2 means it is priceless.
        :return: True if item was added, false otherwise.
        """
        if name in self.library.keys():
            return False
        self.library[name] = value
        return True

    def change_value(self, name: str, new_value: float) -> bool:
        """Alters the value of an item.

        There is no safety on this and should only be called when you are
        certain that it can be called in it's current context

        :param name: Name of the item to replace.
        :param new_value: The value we are changing the item to.
        :return: True if successful, false otherwise (Item does not exist).
        """
        if name in self.library:
            self.library[name] = new_value
            return True
        return False

    def set_save_location(self, location) -> None:
        """Sets the save location of the library.

        Expects the location to be in save_[Server]_[Name].sav format.

        :param location: the location to base this save location off of.
            Expects save_[Server]_[Name].sav format.
        """
        self.save_location = 'Items_' + location[5:-3] + 'csv'
        return

    def save_data(self) -> Optional[str]:
        """Turns the item into a string for saving.
        :return: the string of the item's data.
        """
        if not self.save_location:
            return 'Save Location Not set.'
        data = ''
        for name, value in self.library.items():
            data += "%s,%d,\n" % (name, value)
        with open(self.save_location, 'w') as file:
            file.write(data)
        return

    def load_data(self) -> str:
        """Turns the lines given into data.

        :return: returns any failed lines
        """
        if not self.save_location:
            return "Library not yet saved."
        ret = ''
        with open(self.save_location) as file:
            pass
        return ret
