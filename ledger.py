"""
A ledger program file to manage transactions and loot in games.

Not strongly secure, do not depend on it.
"""
from typing import Union, Mapping, Tuple, NewType
from item import Items
from account import Account


class Ledger:
    """Ledger class which contains and manages both currency and items.

    All valid Commands to be accounted for.
    -- handled in chatbot (creates class instance)
    -+- Ledger [Ledger Name]

    -- Handled by transaction
    -+ [Account] gives [Account]: [Value], [Items...]
    -+ [Account] buys [Items...]
    -+ [Account] sells [Items...]
    -+ [Account] takes from Pot: [Value], [Items...]
    -+ Bank gives [Account]: [Value], [Items...]
    -+ Bank takes from [Account]: [Value], [Items...]
    -+- Set Value [Item]: [Value]

    -- handled in chatbot and calls show_balance()
    -+- [Account] Balance

    -- handled in chatbot and calls add_user()
    -+- Add Account [Account Name]

    -- Handled in chatbot and calls show_rectify()
    -+- Rectify

    -- Handled in chatbot
    -+- New Item [Item]: [Value]
    -+- Delete Item [Item]
    -+- Show History [Lines]
    -+- Show Items
    -+- Save
    -+- Load
    -+- Show Accounts
    -+- Toggle User Lock
    -+- Toggle Store Lock
    -+- Toggle Bank Lock
    -+- Toggle Transaction Lock

    -+- Total Value
    """
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
        self.save_location = "save_%s_%s.sav" % (self.location, self.name)
        # The Library of items as we know it.
        self.library = Items()
        # A number of locks to keep things under control.
        self.user_lock = False
        self.transaction_lock = False
        self.store_lock = False
        self.bank_lock = False
        return

    def new_item(self, name: str, value: float=-1) -> bool:
        """
        Helper function, calls Item.New_item()
        :param name: The Name of the new item.
        :param value: The value of the item.
        :return: True if successful (item does not exist already).
        """
        return self.library.new_item(name=name, value=value)

    def delete_item(self, name: str, key: str) -> bool:
        """
        A helper function to remove an item from the library.
        Calls self.library.delete_item()

        :param name: The item to be deleted.
        :param key: The user's key to ensure it is the admin.
        :return: True if successful, false if anything went wrong.
        """
        if key != self.bank.key:
            return False
        return self.library.delete_item(name)

    def admin_new_item(self, key: str, name: str, value: float) -> bool:
        """
        A helper function to check it is the admin adding the item. Only used
        externally.

        :param key: The key of the user.
        :param name: Name of the item.
        :param value: Value of the item, defaults to unvalued (-1)
        :return: True if item was added, false otherwise.
        """
        if value in [-1, -2] or value >= 0:
            return self.new_item(name, value)
        return False

    def get_account(self, account: str) -> Union[Account, None]:
        """Get's account by name.

        :param account: The account to retrieve
        :return: The user we are looking for, None if it was not found.
        :rtype: Account, None
        """
        if account == "Pot":
            return self.pot
        if self.is_account_name(account):
            for i in range(len(self.users)):
                if account == self.users[i].name:
                    return self.users[i]
        else:
            return None

    def __del__(self) -> None:
        """ When this is deleted it should automatically save. We don't want to
        lose our data do we?
        """
        self.save()
        return

    def show_users(self) -> str:
        """ Returns string of all current accounts.

        :return: All current accounts.
        """
        ret = ''
        for user in self.users:
            ret += user.name + '\n'
        return ret

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
        if name in ['Pot', 'Bank', 'Store']:
            return True
        return name in [user.name for user in self.users]

    def item_list(self) -> str:
        """Gets a list of all items and their current value.

        :return: All the current items and their values.
        """
        ret = ''
        for item, value in self.library.library.items():
            ret += '{}: {}\n'.format(item, value)
        return ret

    def set_value(self, command: str, key: str) -> str:
        """ Sets the value of an item that already exists.

        :param command: The command given by the user.
        :param key: The key of the user to check against.
        :return: A string of anything that happened and if it's successful.
        """
        data = command.lstrip('Set Value ')
        item, value = data.split(':')
        if item not in self.library.library:
            return 'Item Not found.\n'
        item = item.strip()
        value = float(value.strip())
        if key == self.bank.key:
            if value in [-1, -2] or value > 0:
                self.library.change_value(item, value)
            else:
                return 'Value must be -1 for unvalued, -2 ' \
                       'for priceless, or non-negative.'
        elif self.library.library[item] == -1:
            if value < 0:
                return "Value must be non-negative."
            self.library.change_value(item, value)
        self.history.append(command)
        return "Value properly set."

    def transaction(self, command: str, key: str) -> str:
        """ Transaction function.

        This will handle almost all transactions on the basic level, acting as
        a switch between the more appropriate functions.
        :param command: The command to parse.
            Valid commands:
                [Account] gives [Account]: [Value], [Items...]
                [Account] takes from Pot: [Value], [Items...]
                [Account] sells [Items...]
                [Account] buys [Items...]
                Bank gives [Account]: [Value], [Items...]
                Bank takes from [Account]: [Value], [Items...]
                ---- Special Operation ---
                Set Value [Item]: [Value]
            Item must be in [Name]: [Count] format.
        :param key: The key we use for security.
        :return: A string of success or failure, if failure
        error will be given.
        """
        if self.transaction_lock:
            return 'Transactions locked.\n'
        giver = ""
        taker = ""
        action = ""
        value = ""
        items = ""
        ret = ''
        # special op, while it doesn't move anything around, it is still
        # recorded and so put here.
        if command.startswith("Set Value"):
            return self.set_value(command, key)

        words = command.split(" ")
        if len(words) < 3:
            return 'Command not Recognized.\n'
        # giver
        giver = words[0]
        if giver != 'Bank' and not self.is_account_name(giver):
            return 'Account does not exist.\n'
        # taker
        if words[1] == 'gives':
            taker = words[2]
            action = 'give'
        elif words[1] == 'takes' and words[2] == 'from':
            taker = words[3]
            action = 'take'
        elif words[1] in ['buys', 'sells']:
            taker = 'Store'
            action = words[1][:-1]
        else:
            return 'Command not Recognized.\n'
        if ':' in taker:
            taker = taker.replace(':', '')
        if taker not in ['Bank', 'Pot', 'Store'] and not self.is_account_name(taker):
            return "Account does not exist.\n"
        if giver == taker:
            return "Cannot make a transaction with yourself.\n"
        # inputs
        try:
            inputs = ""
            if action in ['give', 'take']:
                inputs = command.split(':', 1)[1]
            elif action in ['buy', 'sell']:
                inputs = command.split(" ", 2)[2]
            inputs = inputs.split(',')
            # value
            if len(inputs) == 1:
                if ':' in inputs[0]:
                    items = inputs
                    value = 0
                else:
                    value = float(inputs[0])
                    items = {}
            elif ':' not in inputs[0]:
                value = float(inputs[0])
                items = inputs[1:]
            else:
                value = 0
                items = inputs
        except IndexError:
            return "Improper Syntax.\n"
        # items
        items_fin = {}
        for item in items:
            if not item:  # if empty, ignore
                continue
            if ':' not in item:
                return "Item must be in [Item]:[Amount] format.\n"
            name, amount = item.split(':')
            items_fin[name.strip()] = int(amount)
        if giver == 'Bank':  # Bank actions  ---------
            if self.bank_lock:
                return 'Bank Locked.\n'
            if self.bank.key != key:
                return "Invalid Key.\n"
            if action == 'give':
                # bank can give items with no value and does not lose anything when
                # it gives
                for item in items_fin:
                    if item not in self.library.library:
                        self.library.new_item(item)
                ret = self.get_account(taker).add(value=value, items=items_fin)
            elif action == 'take':
                # bank can take without reservation.
                ret = self.get_account(taker).take(value=value, items=items_fin)
            if not ret:
                self.history.append(command)
            return ret
        elif taker == 'Store':
            if self.store_lock:
                return "Store Locked.\n"
            dne = ''
            unvalued = ''
            priceless = ''
            ret = ''
            for item in items_fin:
                if item not in self.library.library:
                    dne += "%s," % item
                elif self.library.library[item] == -1:
                    unvalued += "%s," % item
                elif self.library.library[item] == -2:
                    priceless += "%s," % item
            if dne:
               ret += "Items don't exist: %s.\n" % dne
            if unvalued:
                ret += "Items currently unvalued: %s.\n" % unvalued
            if priceless:
                ret += "Priceless Items: %s.\n" % priceless
            if ret:
                return ret
            price = 0
            if action == 'buy':
                price = sum([amount*self.library.library[name] for name, amount in items_fin.items()])
                ret = self.get_account(giver).remove(key=key, value=price)
                if not ret:
                    ret = self.get_account(giver).add(items=items_fin)
                if ret:
                    return ret
            elif action == 'sell':
                price = sum([amount*self.library.library[name] for name, amount in items_fin.items()])
                ret = self.get_account(giver).remove(items=items_fin, key=key)
                if not ret:
                    ret = self.get_account(giver).add(value=price)
                if ret:
                    return ret
            self.history.append(command + " for %d." % price)
        elif taker == 'Pot':
            if action == 'give':
                ret = self.get_account(giver).remove(value=value, items=items_fin, key=key)
                if not ret:
                    ret = self.pot.add(value=value, items=items_fin)
                if ret:
                    return ret
                self.history.append(command)
            elif action == 'take':
                ret = self.pot.remove(value=value, items=items_fin, key="")
                if not ret:
                    ret = self.get_account(giver).add(value=value, items=items_fin)
                if ret:
                    return ret
                self.history.append(command)
        elif taker == 'Bank':
            ret = self.get_account(giver).remove(value=value, items=items_fin,
                                                 key=key)
            if not ret:
                ret = self.bank.add(value=value, items=items_fin)
            if ret:
                return ret
            self.history.append(command)
        else:
            ret = self.get_account(giver).remove(value=value, items=items_fin,
                                                 key=key)
            if not ret:
                ret = self.get_account(taker).add(value=value, items=items_fin)
            if ret:
                return ret
            self.history.append(command)
        return ret

    def show_balance(self, account: str) -> Tuple[float, Mapping[str, int], float, str]:
        """Shows the balance of an account.
        Value and all items, and the total value including items.

        :param account: The account to retrieve
        :param key: The key of the account
        :return: A string of the balance.
        """
        if not self.is_account_name(account):
            return 0, {}, 0, "Account does not exist.\n"
        value = self.get_account(account=account).value
        items = self.get_account(account=account).inventory
        total_value = float(value) + sum([amount*self.library.library[item] if self.library.library[item] >= 0 else 0
                                          for item, amount in items.items()])
        items_str = '\n'
        names = sorted([i for i in items.keys()])
        for name in names:
            items_str += '%s:%d, \n' % (name, items[name])
        return value, items, total_value, "%s has %d and %s Total value of %d.\n" % (account, value, items_str, total_value)

    def total_value(self) -> Tuple[float, Mapping[str, int], float, str]:
        """Retrieves the total value of the pot and all users combined.

        :return: Returns the value, all items in a single dict, total value,
         and a string form of this info.
        """
        value = 0
        coll_items = {}
        for user in self.users:
            value += user.value
            for item, amount in user.inventory.items():
                if item in coll_items:
                    coll_items[item] += amount
                else:
                    coll_items[item] = amount
        # do the same for the pot.
        value += self.pot.value
        for item, amount in self.pot.inventory.items():
            if item in coll_items:
                coll_items[item] += amount
            else:
                coll_items[item] = amount

        total_value = value + sum([amount*self.library.library[item] if self.library.library[item] >= 0 else 0
                                   for item, amount in coll_items.items()])
        items_str = ''
        for item, amount in coll_items.items():
            items_str += '%s:%d, ' % (item, amount)
        items_str = items_str[:-2]
        ret = 'Everyone together holds %d and %s for a total value of %d.\n' % (value, items_str, total_value)
        return value, coll_items, total_value, ret

    def show_rectify(self) -> str:
        """Shows the current value difference between all users and the average.

        This currently only works in value and makes no suggestions on items.

        :return: Each user and the total value they need to reach the average.
        """
        ret = ''
        ave_value = self.total_value()[2]/len(self.users)
        for user in self.users:
            ret += '%s: %d\n' % (user.name, ave_value-self.show_balance(user.name)[2])
        return ret

    def toggle_user_lock(self) -> None:
        """
        Lock user function.
        """
        self.user_lock = not self.user_lock
        return

    def toggle_transaction_lock(self) -> None:
        """
        Lock transactions.
        """
        self.transaction_lock = not self.transaction_lock
        return

    def toggle_store_lock(self) -> None:
        """
        Lock store function.
        """
        self.store_lock = not self.store_lock
        return

    def toggle_bank_lock(self) -> None:
        """
        Lock bank function.
        """
        self.bank_lock = not self.bank_lock
        return

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
            # we save the items separately from our transactions and users.
            # last we write the full transaction history.
            file.write(self.transaction_log())
        # save our smaller data to a config file.
        with open("config_" + self.save_location, 'w') as file:
            file.write(str(self.user_lock) + "\n" + str(self.transaction_lock)
                       + "\n" + str(self.store_lock) + "\n"
                       + str(self.bank_lock))
        self.library.set_save_location(self.save_location)
        self.library.save_data()
        return

    def load_config(self) -> None:
        """Config loading file"""
        with open("config_"+self.save_location, 'r') as file:
            lines = file.readlines()
            self.user_lock = lines[0] == 'True'
            self.transaction_lock = lines[1] == 'True'
            self.store_lock = lines[2] == 'True'
            self.bank_lock = lines[3] == 'True'
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
        self.library.set_save_location(self.save_location)
        self.library.load_data()
        self.history = []
        for line in sections[1].splitlines():
            self.history.append(line)

    def transaction_log(self, transactions: int=0) -> str:
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
