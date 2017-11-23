"""
A ledger program file to manage transactions and loot in games.

Not strongly secure, do not depend on it.
"""
from typing import List, Union, Mapping, Tuple
from random import randint


class Ledger:
    """Ledger class which contains and manages both currency and items."""
    def __init__(self, name: str, server: str, admin: str, key: str,
                 storekey: str) -> None:
        """
        Init function for our Ledger class.

        :param name: name of the ledger.
        :param server: name of the server.
        :param admin: Admin's Name.
        :param key: Admin's Key
        :param storekey: Key to the store (The bot's key.
        """
        # The name of the ledger
        self.name = name
        # The server it belongs to so more then one can be made.
        self.location = server
        # A list of users who exist in the system.
        self.users = []
        # The pot is a non-user, it is a communal pool of value, users can
        # add and remove from it at will, but the pot cannot change anything
        # it is given.
        self.pot = Account("", "Pot", "")
        # Store is a system for users to turn items in for money and vice versa
        # Currently has no safety besides the item must exist and have a value.
        # Safety can be added, requiring admin to check off on transactions
        # with the store but for version 1 this is not being added.
        self.store = Account(admin, "Store", storekey)
        self.store_key = storekey
        # The bank, the account for the admin who can add and take into the
        # system without worry.
        self.bank = Account(admin, "Bank", key)
        # The transaction ledger, what all was traded and in what order.
        self.history = []
        # The location it is saved to.
        self.save_location = "save_%s_%s.sav" % (server, self.name)
        # The Library of items as we know it.
        self.library = Items()
        # A number of locks to keep things under control.
        self.user_lock = False
        self.transaction_lock = False
        self.store_lock = False
        self.bank_lock = False
        return

    def get_account(self, account: str) -> Union[int, None]:
        """Get's account by name.

        :param account: The account to retrieve
        :return:
        """
        if self.is_account_name(account):
            for i in range(len(self.users)):
                if account == self.users[i].name:
                    return i
        else:
            return None

    def __del__(self) -> None:
        """ When this is deleted it should automatically save. We don't want to
        lose our data do we?
        """
        self.save()
        return

    def add_user(self, owner: str, name: str, key: str, value: float=0,
                 items: Mapping[str, int]=None) -> Tuple[bool, str]:
        """Add user function adds the user to the system.
        :param owner: Who owns it
        :param name: the name of the account
        :param key: the owner's key
        :param value: how much they start with
        :param items: A list of items they start with (if any), takes a string
        :return:
        """
        if self.user_lock:
            return False, 'No new Users allowed.\n'
        elif any(i.name == name for i in self.users):
            return False, 'User already exists.\n'
        if value < 0:
            return False, 'Cannot start with negative value.\n'
        if items is None:
            items = dict()
        for item, amount in items.items():
            if amount < 1:
                return (False, 'Cannot start with a negative number of %s.\n'
                        % item)
        for item in items:
            if item not in self.library.library:  # if item doesn't exist add
                self.library.new_item(name=item, value=-1)  # Item at default
        self.users.append(Account(owner, name, key, value, items))
        self.history.append('{0.name} account added with {0.value}gp and '
                            '{1}.'.format(self.users[-1],
                                          self.users[-1].item_list()))
        return True, '%s account added.\n' % name

    def is_account_name(self, name: str) -> bool:
        """Checks if account exists.

        :param name: The name of the account to check.
        :return: True if there, false otherwise.
        """
        return name in [user.name for user in self.users]

    def transaction(self, command: str, key: str) -> str:
        """ Transaction function.

        This will handle almost all transactions on the basic level, acting as
        a switch between the more appropriate functions.
        :param command: The command to parse.
            Valid commands:
                [Account] gives [Account]: [Value], [Items...]
                [Account] takes from Pot: [Value], [Items...]
                [Account] sells [Items...]
                [Account] buys [Items...] for [Values...]
                [Account] Balance
                Bank gives [Account]: [Value], [Items...]
                Bank takes from [Account]: [Value], [Items...]
                ---- Special Operation ---
                Set Value [Item]: [Value]
            Item must be in [Name]: [Count] format.
        :param key: The key we use for security.
        :return: A string of success or failure, if failure
        error will be given.
        """
        giver = ""
        taker = ""
        value = ""
        items = ""
        # special op, while it doesn't move anything around, it is still
        # recorded and so put here.
        if command.startswith("Set Value"):
            return self.set_value(command, key)

        words = command.split(" ")
        giver = words[0]
        if giver != 'Bank' and not self.is_account_name(giver):
            return 'Account does not exist.\n'
        # TODO finish ^ and gut v
        if command.startswith("Bank gives"):
            giver = 'Bank'
            taker = command.lstrip('Bank gives ').split(':', 1)[0]
            inputs = command.split(":", 1)[1].split(',', 1)
            if len(inputs) == 1:
                if ':' in inputs[0]:
                    items = inputs[0]
                else:
                    value = float(inputs[0])
            elif ':' in inputs[0]:
                value = 0
                items = command.split(":", 1)[1]
            else:
                value = float(inputs[0])
                items = inputs[1]
            if self.bank.key != key:
                return "Invalid Key.\n"
            if not self.is_account_name(taker):
                return "Account does not exist.\n"
            # value
            if ':' in value:
                value = 0
            else:
                value = float(value)
            # items
            for pair in items.split(','):
                if not pair:
                    continue
                elif value and pair == inputs.split(',')[0]:
                    continue
                if ':' not in pair:
                    return "Item must be in [Item]:[Amount].\n"
                item, amount = pair.split(':')
                items[item.strip()] = int(amount)
            self.history.append(command)
            ret = self.users[self.get_account(taker)].add(value=value, items=items)
            for item in items:
                if item not in self.library.library:
                    self.library.new_item(item)
            return ret
        elif command.startswith("Bank takes from"):
           return self.bank_takes(command, key)
        if self.is_account_name(command.split(" ", 1)[0]):
            if words[1] == 'gives':
               return self.give_action(command, key)
            elif words[1] == 'takes':
               return self.take_action(command, key)
            elif words[1] == 'sells':
               return self.sell_items(command, key)
            elif words[1] == 'buys':
               return self.buy_items(command, key)
            elif words[1] == 'Balance':
                return self.show_balance(words[1], key)
            else:
                return 'Command Not found.\n'
        else:
            return "Account does not exist.\n"

    def parse_item_list(self, items: str) -> bool:
        """ Parses a string of items into a dict.
        :param items: The item string to parse.
                Format: [Item Name]:[Item count] [, Next item]
        :return: True if successful, False otherwise.
        """

        return

    def total_value(self):
        pass

    def show_rectify(self):
        pass

    def save(self) -> None:
        """ Save function. Can be called as needed, guaranteed to be called on
        close.
        """
        with open(self.save_location, 'w') as file:
            # first lines should have the current totals for each account
            # All small lines are separated by \n big seperations by \n\n
            file.write(self.bank.save_data()+"\n")
            file.write(self.store.save_data()+'\n')
            file.write(self.pot.save_data()+'\n')
            for i in self.users:
                file.write(i.save_data()+'\n')
            file.write("\n\n")
            # second is tha values of any items that exist. If it's value is
            # not found then the item is currently unvalued.
            file.write(self.library.save_data() + "\n")
            file.write('\n\n')
            # last we write the full transaction history.
            file.write(self.transaction_log())
        # save our smaller data to a config file.
        with open("config_" + self.save_location, 'w') as file:
            file.write(str(self.user_lock) + "\n" + str(self.transaction_lock)
                       + "\n" + str(self.store_lock) + "\n"
                       + str(self.bank_lock))
        return

    def load_config(self) -> None:
        """Config loading file"""
        with open("config_"+self.save_location, 'r') as file:
            lines = file.readlines()
            self.user_lock = bool(lines[0])
            self.transaction_lock = bool(lines[1])
            self.store_lock = bool(lines[2])
            self.bank_lock = bool(lines[3])
        return

    def load_save(self) -> None:
        """Load save file."""
        with open(self.save_location, 'r') as file:
            data = file.read()
        sections = data.split('\n\n')
        lines = sections[0].splitlines()
        self.bank.load_data(lines[0])
        self.store.load_data(lines[1])
        self.pot.load_data(lines[2])
        for line in lines[2:]:
            self.users.append(Account())
            self.users[-1].load_data(line)
        self.library.load_data(sections[1])
        self.history = []
        for line in sections[2].splitlines():
            self.history.append(line)

    def transaction_log(self, transactions=0):
        """Gets the history and returns it in readable format.
        :param int transactions: number of transactions to show, 0 shows all.
        :return: The history, delineated by newlines.
        """
        ret = ''
        if 0 < transactions < len(self.history):
            for i in self.history[-transactions:]:
                ret += i + '\n'
        else:
            for i in self.history:
                ret += i + '\n'
        return ret


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

    def remove(self, key: str, value: float, items: Mapping[str, int]) -> str:
        """
        Remove something from the account.

        Checks for validity of removal and then follows through to the best of
        it's abilities.

        :param key: The key to check for security.
        :param value: How much currency is being removed.
        :param items: What items and how many of them to remove.
        :return: Any errors or problems that were run into.
        """
        if key != self.key or self.key == "":
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


class Items:
    """The Library of all items that currently exist.

    Contains all our items, names for items should be unique at all times.

    Dict contains name (str) and Value (float) pairs.
    """
    def __init__(self) -> None:
        self.library = dict()
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

    def save_data(self) -> str:
        """Turns the item into a string for saving.
        :return: the string of the item's data.
        """
        ret = ''
        for name, value in self.library.items():
            ret += "%s\t%d\n" % (name, value)
        return ret[:-1]

    def load_data(self, lines: str) -> str:
        """Turns the lines given into data.

        :param lines: the lines to load, must be in [item name]\t[item value]
                     format.
        :return: returns any failed lines
        """
        ret = ''
        for line in lines.splitlines():
            if '\t' not in line:
                ret += line + '\n'
            else:
                name, value = line.split('\t')
                self.library[name] = float(value)
        return ret
