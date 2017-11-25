"""
File for account class.
:author: Jeremy Daugherty
"""

from typing import Tuple, Union, Mapping


class Account:
    """Account class, contains and checks that it is the user removing stuff
    from it. It will contain raw numerical value and a list of items.

    It checks against the key to see if the user is who they say they are.
    """
    def __init__(self, owner: str = "", name: str = "", key: str = "",
                 value: float = 0,
                 inventory: Union[Mapping[str, int], None] = None):
        # Who owns this account
        self.owner = owner
        # The name of the account
        self.name = name
        # The key they check against.
        self.key = key
        # Raw value contained in whatever currency is being used.
        self.value = value
        # Unliquidated items owned. A map of inventory[Name]->amount.
        if inventory is None:
            inventory = dict()
        self.inventory = inventory
        return

    def save_data(self) -> str:
        """Takes the account and puts in into a form that can be saved.

        :return: A string of it's data.
        """
        ret = self.owner + "\t" + self.name + "\t" + self.key + "\t"
        ret += str(self.value) + "\t" + self.item_list()
        return ret

    def load_data(self, line: str) -> None:
        """Load data function, no check, if it don't work it's because it's
        broken.

        :param line: The line to parse and load from.
        """
        data = line.split('\t')
        self.owner = data[0]
        self.name = data[1]
        self.key = data[2]
        self.value = float(data[3])
        items = data[4]
        for item in items.split(','):
            name, amount = item.split(':')
            self.inventory[name] = float(amount)
        return

    def item_list(self) -> str:
        """
        Returns the list of items in a string. Items are separated by commas.

        :return: The string of the account's items listed.
        """
        ret = ''
        for item, amount in self.inventory.items():
            ret += "%s:%d," % (item, amount)
        return ret[:-1]

    def add(self, value: float=0, items: Mapping[str, int]=None) -> str:
        """Adds something to the account.

        This will add something to the account and has no safety measures
        because who doesn't like free stuff?

        .. warning:: Item's existence cannot be checked here, must be checked
        beforehand.

        :param value: What is being added to the value. Must be >0
        :param items: What Items are being added to their list.
                Amount must be >0
        :return: Returns an empty string if successful, what went wrong
        otherwise.
        """
        if not value and items is None:  # sanity check
            return "Nothing given.\n"
        if value < 0:  # if negative value
            return "Value cannot be negative.\n"
        else:
            self.value += value
        if items is None:
            return ""
        for item, amount in items.items():
            if amount < 1:
                return "Cannot add a negative number of %s to inventory.\n" %\
                       item
        for item, amount in items.items():
            if item in self.inventory:
                self.inventory[item] += amount
            else:
                self.inventory[item] = amount
        return ""

    def remove(self, key: str, value: float=0, items: Mapping[str, int]=None) -> str:
        """
        Remove something from the account.

        Checks for validity of removal and then follows through to the best of
        it's abilities.

        :param key: The key to check for security.
        :param value: How much currency is being removed.
        :param items: What items and how many of them to remove.
        :return: Any errors or problems that were run into.
        """
        if key != self.key:
            return "Invalid Key, you are not %s.\n" % self.name
        return self.take(value, items)

    def take(self, value: float=0, items: Mapping[str, int] = None) -> str:
        """
        Take from the account what has been passed in.

        :param value: How much currency to remove.
        :param items: A dict of items to be removed and how many of each.
        :return: If ANYTHING goes wrong it will return a non-empty string.
        """
        if not value and not items:
            return "Nothing Passed. Try again.\n"
        if value < 0:
            return "You cannot remove a negative number!\n"
        elif value > self.value:
            return "You don't have enough money.\n"
        if items is not None:
            for item, amount in items.items():
                if item not in self.inventory:
                    return "You don't have any %s(s).\n" % item
                elif self.inventory[item] < amount:
                    return "You don't have enough %s(s).\n" % item
                elif amount < 1:
                    return "You cannot remove less than 1 item from an " \
                           "Inventory.\n"
            for item, amount in items.items():
                self.inventory[item] -= amount
                if self.inventory[item] == 0:
                    self.inventory.pop(item)
        self.value -= value
        return ""

    def balance(self) -> Tuple[float, str]:
        """Balance checking formula, returns everything owned by the account.

        :return: Returns a tuple containing the value of the account and all
        items.
        """
        return self.value, self.item_list()
