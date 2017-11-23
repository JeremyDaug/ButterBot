import unittest
import ledger


class TestItems(unittest.TestCase):
    def setUp(self):
        self.library = ledger.Items()
        self.library.new_item('Normal', 1)
        self.library.new_item('Unvalued', -1)
        self.library.new_item('Priceless', -2)
        return

    def test_new_item_true(self):
        self.assertTrue(self.library.new_item('Bolt', 20))

    def test_new_item_false(self):
        self.assertFalse(self.library.new_item('Normal'))

    def test_change_value_true(self):
        self.assertTrue(self.library.change_value('Normal', 2))

    def test_change_value_false(self):
        self.assertFalse(self.library.change_value('DNE', 2))

    def test_save_data(self):
        save1 = self.library.save_data()
        print('\n'+save1)
        save2 = self.library.save_data()
        print('\n'+save2+'\n')
        self.assertTrue(save1, save2)

    def test_load_data(self):
        save = self.library.save_data()
        with open('Item_test.sav', 'w') as file:
            file.write(save)

        new_lib = ledger.Items()
        with open('Item_test.sav', 'r') as file:
            load = file.read()
            new_lib.load_data(load)
            print('\n'+load)
            print(new_lib.save_data())

        for item, value in new_lib.library.items():
            with self.subTest(item):
                self.assertTrue(item in self.library.library)
            with self.subTest(value):
                self.assertTrue(value == self.library.library[item])

    def test_load_data_fail(self):
        with open('Item_test.sav', 'w') as file:
            file.write('Silly Goose: 15000\nthis should work\t10')

        new_lib = ledger.Items()

        with open('Item_test.sav', 'r') as file:
            data = file.read()
            print(data)
            self.assertIsNotNone(new_lib.load_data(data))
            print(new_lib.save_data())


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.acc = ledger.Account('TestUser', 'TestName', 'TestKey', 100,
                                  {"Test": 1})

    def test_balance(self):
        value, items = self.acc.balance()
        self.assertEqual(value, 100)
        self.assertEqual(items, "Test:1")

    def test_item_list(self):
        test1 = self.acc.item_list()
        print(test1)
        self.assertEqual(test1, self.acc.item_list())
        self.acc.add(items={"New Item": 1})
        test2 = self.acc.item_list()
        print(test2)
        self.assertEqual(test2, self.acc.item_list())

    def test_take_nothing(self):
        self.assertEqual(self.acc.take(), "Nothing Passed. Try again.\n")

    def test_take_negative(self):
        self.assertEqual(self.acc.take(value=-1),
                         "You cannot remove a negative number!\n")

    def test_take_too_much(self):
        self.assertEqual(self.acc.take(value=101),
                         'You don\'t have enough money.\n')

    def test_take_wrong_item(self):
        self.assertEqual(self.acc.take(items={'DNE': 1}),
                         "You don't have any DNE(s).\n")

    def test_take_too_many_items(self):
        self.assertEqual(self.acc.take(items={"Test": 2}),
                         "You don't have enough Test(s).\n")

    def test_take_too_few_items(self):
        self.assertEqual(self.acc.take(items={"Test": -1}),
                         "You cannot remove less than 1 item from an " +
                         "Inventory.\n")

    def test_take_value(self):
        self.assertEqual(self.acc.take(value=50), "")
        self.assertEqual(self.acc.value, 50)

    def test_take_item(self):
        self.assertEqual(self.acc.take(items={'Test': 1}), "")
        self.assertEqual(self.acc.inventory, dict())

    def test_remove_success(self):
        self.assertEqual(self.acc.remove(self.acc.key, 50, {'Test': 1}), "")
        self.assertEqual(self.acc.value, 50)
        self.assertEqual(self.acc.inventory, dict())

    def test_remove_failure(self):
        self.assertEqual(self.acc.remove("NOT KEY", 50, {'Test': 1}),
                         "Invalid Key, you are not TestName.\n")
        self.assertEqual(self.acc.value, 100)
        self.assertEqual(self.acc.inventory, {'Test': 1})

    def test_add_value(self):
        self.assertEqual(self.acc.add(value=10), "")
        self.assertEqual(self.acc.value, 110)
        self.assertEqual(self.acc.inventory, {'Test': 1})

    def test_add_existing_item(self):
        self.assertEqual(self.acc.add(items={"Test": 1}), "")
        self.assertEqual(self.acc.value, 100)
        self.assertEqual(self.acc.inventory, {"Test": 2})

    def test_add_new_item(self):
        self.assertEqual(self.acc.add(items={"TEST": 1}), "")
        self.assertEqual(self.acc.value, 100)
        self.assertEqual(self.acc.inventory, {"Test": 1, "TEST": 1})

    def test_add_negative_value(self):
        self.assertEqual(self.acc.add(value=-10), "Value cannot be negative.\n")
        self.assertEqual(self.acc.value, 100)
        self.assertEqual(self.acc.inventory, {"Test": 1})

    def test_add_nothing(self):
        self.assertEqual(self.acc.add(), "Nothing given.\n")
        self.assertEqual(self.acc.value, 100)
        self.assertEqual(self.acc.inventory, {"Test": 1})

    def test_add_negative_item(self):
        self.assertEqual(self.acc.add(items={"Test": -1}),
                         "Cannot add a negative number of Test to inventory.\n"
                         )
        self.assertEqual(self.acc.value, 100)
        self.assertEqual(self.acc.inventory, {"Test": 1})

    def test_save(self):
        print('\n' + self.acc.save_data())
        self.assertEqual(self.acc.save_data(), self.acc.save_data())

    def test_load(self):
        with open('Test_Account.sav', 'w') as file:
            file.write(self.acc.save_data())

        new_acc = ledger.Account()
        with open('Test_account.sav', 'r') as file:
            new_acc.load_data(file.read())

        self.assertEqual(new_acc.owner, self.acc.owner)
        self.assertEqual(new_acc.name, self.acc.name)
        self.assertEqual(new_acc.key, self.acc.key)
        self.assertEqual(new_acc.value, self.acc.value)
        self.assertEqual(new_acc.inventory, self.acc.inventory)


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.ledger = ledger.Ledger("Test", "Test", "TestAdmin", "TestKey",
                                    "TestStoreKey")
        self.ledger.add_user("TestUser", "TestAccount",
                             "TestUserKey", 100, {'Test': 1})

    def test_add_user(self):
        self.assertEqual(self.ledger.add_user("TestUser1", "TestAccount1",
                                              "TestUserKey1", 100, {'Test': 1})
                         , (True, "TestAccount1 account added.\n"))
        self.assertEqual(self.ledger.users[-1].owner, "TestUser1")
        self.assertEqual(self.ledger.users[-1].name, "TestAccount1")
        self.assertEqual(self.ledger.users[-1].key, "TestUserKey1")
        self.assertEqual(self.ledger.users[-1].value, 100)
        self.assertEqual(self.ledger.users[-1].inventory, {"Test": 1})
        self.assertTrue('Test' in self.ledger.library.library)
        print('\n' + str(self.ledger.history))

    def test_add_existing_user(self):
        self.assertEqual(self.ledger.add_user("TestUser", "TestAccount",
                                              "TestUserKey"),
                         (False, "User already exists.\n"))

    def test_new_users_blocked(self):
        self.ledger.user_lock = True
        self.assertTrue(self.ledger.user_lock)
        self.assertEqual(self.ledger.add_user("TestUser", "TestAccount",
                                              "TestUserKey"),
                         (False, "No new Users allowed.\n"))

    def test_new_user_negative_value(self):
        self.assertEqual(self.ledger.add_user("TestUser1", "TestAccount1",
                                              "TestUserKey1", -100)
                         , (False, "Cannot start with negative value.\n"))
        self.assertFalse(self.ledger.users[-1].name == "TestUser1")

    def test_new_user_negative_item(self):
        self.assertEqual(self.ledger.add_user("TestUser1", "TestAccount1",
                                              "TestUserKey1",
                                              items={'Test': -1})
                         , (False,
                            "Cannot start with a negative number of Test.\n"))

    def test_is_account_name_true(self):
        self.assertTrue(self.ledger.is_account_name("TestAccount"))

    def test_is_account_name_false(self):
        self.assertFalse(self.ledger.is_account_name("DNE"))

    def test_bank_gives_value(self):
        self.assertEqual(
            self.ledger.transaction("Bank gives TestAccount: 100",
                                    'TestKey'),
            "")
        self.assertEqual(self.ledger.users[-1].value, 200)

    def test_bank_gives_item(self):
        self.assertEqual(
            self.ledger.transaction("Bank gives TestAccount: VAT:1",
                                    'TestKey'),
            "")
        print(self.ledger.users[self.ledger.get_account(
                'TestAccount')].inventory)
        self.assertTrue(
            'VAT' in self.ledger.users[self.ledger.get_account(
                'TestAccount')].inventory)
        self.assertEqual(self.ledger.users[-1].inventory['VAT'], 1)

    def test_bank_gives_items(self):
        self.assertEqual(
            self.ledger.transaction(
                "Bank gives TestAccount: Item1:1, Item2: 4, Item9:10",
                'TestKey'), "")
        self.assertTrue('Item1' in self.ledger.users[-1].inventory)
        self.assertTrue('Item2' in self.ledger.users[-1].inventory)
        self.assertTrue('Item9' in self.ledger.users[-1].inventory)
        self.assertEqual(self.ledger.users[-1].inventory['Item1'], 1)
        self.assertEqual(self.ledger.users[-1].inventory['Item2'], 4)
        self.assertEqual(self.ledger.users[-1].inventory['Item9'], 10)

    def test_bank_gives_value_and_items(self):
        self.assertEquals(
            self.ledger.transaction(
                "Bank gives TestAccount: 100, Item1:1, Item2: 4,",
                'TestKey'), "")
        self.assertEqual(
            self.ledger.users[-1].value, 200
        )
        self.assertEqual(self.ledger.users[-1].inventory['Item1'], 1)
        self.assertEqual(self.ledger.users[-1].inventory['Item2'], 4)

    def test_bank_gives_negative_value(self):
        self.assertEqual(
            self.ledger.transaction("Bank gives TestAccount: -100", 'TestKey'),
            "Value cannot be negative.\n")

    def test_bank_gives_negative_item(self):
        self.assertEqual(self.ledger.transaction(
            "Bank gives TestAccount: Item1:-1",
            'TestKey'),
            "Cannot add a negative number of Item1 to inventory.\n")

    def test_bank_gives_bad_account(self):
        self.assertEqual(self.ledger.transaction("Bank gives Test: 100",
                                                 'TestKey'),
                         "Account does not exist.\n")

    def test_bank_gives_bad_syntax(self):
        self.assertEqual(self.ledger.transaction(
            "Bank gives TestAccount: 100, 50", 'TestKey'),
                         "Item must be in [Item]:[Amount].\n")

    def test_bank_invalid_key(self):
        self.assertEqual(
            self.ledger.transaction("Bank gives TestAccount: 100, 50", 'Key'),
            "Invalid Key.\n")


if __name__ == '__main__':
    unittest.main()
