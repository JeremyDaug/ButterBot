import unittest
import ledger
from item import Items


class TestItems(unittest.TestCase):
    def setUp(self):
        self.library = ledger.Items()
        self.library.set_save_location('save_TestServer_TestName.sav')
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
        self.library.set_save_location("save_TestServer_TestName.sav")
        self.library.save_data()
        new_lib = Items()
        new_lib.set_save_location("save_TestServer_TestName.sav")
        new_lib.load_data()
        self.assertTrue(self.library.library == new_lib.library)

    def test_load_data(self):
        with open('Items_TestServer_TestName.csv', 'w') as file:
            file.write('Test1, 1,\nTest2,10,\nTest3,-1,\nTest4,-2,\n')
        new_lib = Items()
        new_lib.set_save_location('save_TestServer_TestName.sav')
        new_lib.load_data()
        self.assertTrue('Test1' in new_lib.library)
        self.assertTrue('Test2' in new_lib.library)
        self.assertTrue('Test3' in new_lib.library)
        self.assertTrue('Test4' in new_lib.library)
        self.assertTrue(new_lib.library['Test1'] == 1)
        self.assertTrue(new_lib.library['Test2'] == 10)
        self.assertTrue(new_lib.library['Test3'] == -1)
        self.assertTrue(new_lib.library['Test4'] == -2)

    def test_load_data_fail(self):
        with open('Item_test.sav', 'w') as file:
            file.write('Silly Goose: 15000\nthis should work\t10')

        new_lib = ledger.Items()

        with open('Item_test.sav', 'r') as file:
            data = file.read()
            print(data)
            self.assertEqual(new_lib.load_data(),
                             'Save Location Not Set.\n')
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
        self.ledger.library.new_item('Test', 100)
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

    def test_transaction_bank_gives_value(self):
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
        print(self.ledger.get_account(
                'TestAccount').inventory)
        self.assertTrue(
            'VAT' in self.ledger.get_account(
                'TestAccount').inventory)
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
        self.assertEqual(
            self.ledger.transaction(
                "Bank gives TestAccount: 100,Item1:1,Item2:  4,",
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

    def test_transaction_negative_item(self):
        self.assertEqual(self.ledger.transaction(
            "Bank gives TestAccount: Item1:-1",
            'TestKey'),
            "Cannot add a negative number of Item1 to inventory.\n")

    def test_transaction_bad_account(self):
        self.assertEqual(self.ledger.transaction("Bank gives Test: 100",
                                                 'TestKey'),
                         "Account does not exist.\n")
        self.assertEqual(self.ledger.transaction("Test gives Bank: 100",
                                                 'TestKey'),
                         "Account does not exist.\n")

    def test_transaction_syntax(self):
        self.assertEqual(self.ledger.transaction(
            "Bank gives TestAccount: 100, 50", 'TestKey'),
                         "Item must be in [Item]:[Amount] format.\n")

    def test_transaction_bank_invalid_key(self):
        self.assertEqual(
            self.ledger.transaction("Bank gives TestAccount: 100", 'Key'),
            "Invalid Key.\n")

    def test_store_buy_item(self):
        self.ledger.library.new_item('Test1', 100)
        self.assertEqual(
            self.ledger.transaction("TestAccount buys Test1:1", 'TestUserKey'),
            "")
        self.assertEqual(
            self.ledger.get_account('TestAccount').inventory['Test1'], 1
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').value, 0
        )

    def test_store_sell_item(self):
        self.ledger.new_item('Test1', 100)
        print(self.ledger.transaction("Bank gives TestAccount: Test1:2", 'TestKey'))
        self.assertEqual(
            self.ledger.get_account('TestAccount').inventory["Test1"],
            2
        )
        self.assertEqual(
            self.ledger.transaction("TestAccount sells Test1:1", 'TestUserKey'),
            ""
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').value,
            200
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').inventory['Test1'],
            1
        )

    def test_store_locked(self):
        self.ledger.store_lock = True
        self.assertEqual(
            self.ledger.transaction('TestAccount sells Test:1', 'TestUserKey'),
            'Store Locked.\n'
        )

    def test_bank_gives_pot(self):
        self.assertEqual(
            self.ledger.transaction("Bank gives Pot: 100", 'TestKey'),
            ''
        )
        self.assertEqual(
            self.ledger.get_account('Pot').value,
            100
        )
        self.ledger.new_item('Test1', 100)
        self.assertEqual(
            self.ledger.transaction("Bank gives Pot: Test1:1", 'TestKey'),
            ''
        )
        self.assertEqual(
            self.ledger.get_account('Pot').inventory['Test1'],
            1
        )

    def test_give_pot(self):
        self.assertEqual(
            self.ledger.transaction('TestAccount gives Pot: 100, Test:1', 'TestUserKey'),
            ''
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').value,
            0
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').inventory,
            {}
        )
        self.assertEqual(
            self.ledger.get_account('Pot').value,
            100
        )
        self.assertEqual(
            self.ledger.get_account('Pot').inventory['Test'],
            1
        )

    def test_take_pot(self):
        self.assertEqual(
            self.ledger.transaction('Bank gives Pot: 100, Test:1', 'TestKey'),
            ''
        )
        self.assertEqual(
            self.ledger.get_account('Pot').value,
            100
        )
        self.assertEqual(
            self.ledger.get_account('Pot').inventory['Test'],
            1
        )
        self.assertEqual(
            self.ledger.transaction('TestAccount takes from Pot: 100, Test:1', 'TestUserAccount'),
            ''
        )
        self.assertEqual(
            self.ledger.get_account('Pot').value,
            0
        )
        self.assertEqual(
            self.ledger.get_account('Pot').inventory,
            {}
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').value,
            200
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').inventory['Test'],
            2
        )

    def test_account_gives_account(self):
        self.assertEqual(
            self.ledger.add_user("TestUser2", 'TestAccount2', 'TestUserKey2',
                                 100, {'Test': 1}),
            (True, 'TestAccount2 account added.\n')
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount2').value,
            100
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount2').inventory['Test'],
            1
        )
        self.assertEqual(
            self.ledger.transaction('TestAccount gives TestAccount2: 100, Test:1', 'TestUserKey'),
            ''
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').value,
            0
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount').inventory,
            {}
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount2').value,
            200
        )
        self.assertEqual(
            self.ledger.get_account('TestAccount2').inventory['Test'],
            2
        )

    def test_show_balance(self):
        self.assertEqual(
            self.ledger.show_balance('TestAccount'),
            (100, {'Test': 1}, 200, 'TestAccount has 100 and Test:1, for a total value of 200.\n')
        )
        self.assertEqual(
            self.ledger.transaction('Bank gives TestAccount: 100', 'TestKey'),
            ''
        )
        self.assertEqual(
            self.ledger.show_balance('TestAccount'),
            (200, {'Test': 1}, 300, 'TestAccount has 200 and Test:1, for a total value of 300.\n')
        )

    def test_show_pot_balance(self):
        self.assertEqual(
            self.ledger.transaction('Bank gives Pot: 100, Test:1', 'TestKey'),
            ''
        )
        self.assertEqual(
            self.ledger.show_balance('Pot'),
            (100, {'Test': 1}, 200, 'Pot has 100 and Test:1, for a total value of 200.\n')
        )

    def test_show_balance_invalid_account(self):
        self.assertEqual(
            self.ledger.show_balance('DNEAccount')[-1],
            'Account does not exist.\n'
        )

    def test_show_total_value(self):
        self.assertEqual(
            self.ledger.total_value(),
            (100, {'Test': 1}, 200,
             'Everyone together holds 100 and Test:1 for a total value of 200.\n')
        )

    def test_show_rectify(self):
        self.assertEqual(
            self.ledger.show_rectify(),
            "TestAccount: 0\n"
        )
        self.assertEqual(
            self.ledger.transaction('Bank gives Pot: 100', 'TestKey'),
            ''
        )
        self.assertEqual(
            self.ledger.show_rectify(),
            'TestAccount: 100\n'
        )

    def test_transaction_log(self):
        self.ledger.transaction('Bank gives TestAccount1: 100', 'TestKey')
        self.ledger.add_user("TestUser2", 'TestAccount2', 'TestUserKey2')
        print(self.ledger.history)
        print(self.ledger.transaction_log(1))

    def test_save_and_load(self):
        self.ledger.save()
        data = ''
        with open(self.ledger.save_location, 'r') as file:
            data = file.read()
        print(data)
        self.ledger.users = []
        self.assertEqual

    def test_give_bank_item(self):
        self.assertEqual(
            self.ledger.transaction('TestAccount gives Bank: 100',
                                    'TestUserKey'),
            ''
        )


if __name__ == '__main__':
    unittest.main()
