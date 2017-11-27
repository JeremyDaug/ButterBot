import discord
import asyncio
import rolling
import voting
import pickle
from ledger import Ledger
import string
client = discord.Client()

VERSION = '1.1.1'

qwk_help = """For more specific help type help [topic].
Topics are :
- dice
- voting
- request
- ledger
- ledger_management
- ledger_commands"""

dice_help = """The expression works like a simple equation parser with some extra operators.

The following operators are listed in order of precedence.

The dice (‘d’) operator takes an amount (A) and a number of sides (S), and returns a list of A random numbers between 1 and S. For example: 4d6 may return [6, 3, 2, 4].

If A is not specified, it is assumed you want to roll a single die. d6 is equivalent to 1d6.

Basic integer operations are available: 16 / 8 * 4 + 2 - 1 -> 9.

A set of rolls can be turned into an integer with the total (t) operator. 6d1t will return 6 instead of [1, 1, 1, 1, 1, 1]. Applying integer operations to a list of rolls will total them automatically.

A set of dice rolls can be sorted with the sort (s) operator. 4d6s will not change the return value, but the dice will be sorted from lowest to highest.

The lowest or highest rolls can be selected with ^ and v. 6d6^3 will keep the highest 3 rolls, whereas 6d6v3 will select the lowest 3 rolls."""

voting_help = """Syntax To create Vote
Create Vote ID:[Num] Q:[question] O:[option1, option2, ...] N:[Num Votes]
ID: ID value of the vote.
Q: Question raised or asked, try to keep it simple.
O: Options in a comma separated list.
N: Number of votes each person has. If value is greater then number of options then 1 vote per option is allowed.

Syntax to Vote :
Vote:[ID]:[option1, option2, ...]

List all options you vote on, if you give more options then votes it will say
so. You cannot vote for the same thing twice.

To Delete Vote :
Delete Vote:[ID]

Deletes the vote of ID if possible.

To Save :
Save Votes

Saves votes to file.

To Load :
Load Votes

To Show Current Voting IDs :
Show Vote IDs

To Show Vote Results :
Show Vote: [ID]"""

request_help = """Syntax:
Request: [Request]

This is for requesting changes or features for butter bot.

It will save them so that My Creator can act on them later.

Thank you for the request."""

ledger_help_basic = """Syntax:
A Ledger created by calling.

.L Ledger [Ledger Name]

This will create a ledger with you as the admin of it.
If the ledger already exists in the server you cannot make it again.
I do not suggest creating more then one per server as messages may get mixed.
If you cannot follow through with a transaction in part it will not allow
the transaction as a whole.

Commands once a ledger is made are as follows.

--Adding an account:
.t Add Account [Account Name]

Your account name is the name you will call to make transactions.
Try to remember it.

--Transaction:
.t [Account] gives [Account]: [Value], [Items...]

Value can be any number. Items must be in [Name]: [Amount] format.
Value and all items must be separated by commas.
You can drop value or give as many items as you wish, but you can only give
value first.
EX. Alice gives Bob: 100
    Alic gives Bob: Sword:1, Shield:1
    Alice gives Bob: 100, Sword:1, Bat:1

-- Buying and selling.
.t [Account] buys [Items...]
.t [Account] sells [Items..]

Items follows the same rules as transactions. You may buy/sell as many as you
wish at a time. The store has infinite items and always has money to buy so
don't worry about stuff running out.

-- Taking from the Pot:

.t [Account] takes from Pot: [Value], [Items...]

This works as the give transaction from earlier, but anyone can take from the
pot.

-- Bank actions:
.t Bank gives [Account]: [Value], [Items...]
.t Bank takes from [Account]: [Value], [Items...]

The Bank may give and take infinitely, but only the admin may do so. The bank
is how all items and currency is added to the system. As a note, anyone may
give to the bank as a way to remove money from the system.

Banks may give items even if said items do not exist, they are automatically
marked as unvalued.
"""

ledger_help_management = """Management Actions:
.t [Account] Balance

Shows you the balance of an account, all money and items that an account has.
Anyone may use this.

.t Rectify

Takes all the current money and items in all accounts, and the pot, and shows
the amount of money each account needs to have to average them all out. Anyone
may use this.

.t Set Value [Item]: [Value]

Sets the value of an item to another value. Anyone can use this if the item has
no value. If an items already has a value only the admin can change it. 

.t New Item [Item]: [Value]

This will add a new item to the system with the value given.
[Item] is the name of the item. [Value] is the value of the item. Currently,
only the admin may do this action.

.t Show History [Lines]

This will show you [Lines] number of previous transactions. If lines is not
given it will show you all of them. Please use wisely.

.t Show Items

Shows all items that currently exist. Again, use with caution as it may take
up lots of space.

.t Total Value

Shows all of the current money and items in the system. Does not show
individual accounts, only the sum of the system.

.t Delete Item [Item]

Deletes an item from the library. Only usable by the admin.

--Final Notes:

Don't go crazy with names. There's no guarantee that on what will happen if you
include spaces or : in names. You might get away with other symbols, but please
don't be crazy.

If there is an error, please send a request with info on it.
"""

ledger_help_commands = """Condensed Commands:
** items are in the format '[Name]: [Amount],'
 Set Value Expects '[Item Name]: [Item Value]' **
-- .t Ledger [New_Ledger_Name]
-- .t Add Account [Account Name]
-- .t [Account] gives [Account]: [Value], [Items...]
-- .t [Account] takes from Pot: [Value], [Items...]
-- .t [Account] buys [Items...]
-- .t [Account] sells [Items...]
-- .t Bank gives [Account]: [Value], [Items...]
-- .t Bank takes [Account]: [Value], [Items...]
-- .t Set Value [Item]: [Value]
-- .t [Account] Balance
-- .t Rectify
-- .t New Item [Item]: [Value]
-- .t Delete Item [Item] 
-- .t Show History [Number of Lines]
-- .t Show Items
-- .t Total Value
-- .t Save
-- .t Load [Name]
-- .t Show Accounts

Non-implemented commands. 
-- .t toggle [lock] lock
"""  # TODO Add Toggle Lock Commands


admin = '200818099547668490'

votes = voting.voting()
da_books = {}


@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print('Version %s' % VERSION)
    print(client.user.id)
    print('-----------------')


def log(*args):
    print('-----------------')
    for arg in args:
        print(arg)
    return


@client.event
async def on_message(message):
    # if message.author.id != client.user.id:
    #     await client.send_typing(message.channel)
    log(message.author.name, message.channel, message.content)
    sp = message.content.split()
    if sp[0] == '<@{}>'.format(client.user.id):
        if len(sp) <= 1:
            await client.send_message(message.channel, 'What do you want?')
        elif 'real purpose' in message.content.lower():
            await client.send_message(message.channel,
                                      'To roll dice and collect votes.')
        elif 'purpose' in message.content.lower():
            await client.send_message(message.channel, 'To pass butter')
        elif 'help' == sp[1].lower():
            if len(sp) <= 2:
                await client.send_message(message.channel, qwk_help)
            elif sp[2].lower() == 'dice':
                await client.send_message(message.channel, dice_help)
            elif sp[2].lower() == 'voting':
                await client.send_message(message.channel, voting_help)
            elif sp[2].lower() == 'request':
                await client.send_message(message.channel, request_help)
            elif sp[2].lower() == 'ledger':
                await client.send_message(message.channel, ledger_help_basic)
            elif sp[2].lower() == 'ledger_management':
                await client.send_message(message.channel,
                                          ledger_help_management)
            elif sp[2].lower() == 'ledger_commands':
                await client.send_message(message.channel,
                                          ledger_help_commands)
            else:
                await client.send_message(message.channel, qwk_help)
        elif 'version' in message.content.lower():
            await client.send_message(message.channel, VERSION)
        elif 'Sepuku' in message.content:
            if message.author.id == admin:
                client.logout()
                client.close()
            else:
                await client.send_message(message.channel, 'I live to serve. But you are not my admin.')
    elif message.content.startswith('.r '):  # rolling dice.
        await client.send_message(message.channel, rolling.roll(message.content[3:]))
    elif message.content.startswith('.L'):  # Create ledger
        name = message.content.split(' ')
        if len(name) != 3:
            await client.send_message(message.channel,
                                      "Must give a name to the ledger "
                                      "and cannot have whitespace.")
        else:
            da_books[message.server] = Ledger(name[2], message.server,
                                              message.author.name,
                                              message.author.id,
                                              "%sStoreKey" % message.author.id)
            await client.send_message(message.channel,
                                      "Ledger Created.")

    elif message.content.startswith('.t'):  # ledger actions.
        command = message.content[3:]
        if command.startswith('Load '):
            name = command.lstrip('Load ')
            if True in [c in name for c in string.whitespace]:
                await client.send_message(message.channel,
                                          'Name cannot contain whitespace.')
            else:
                da_books[message.server] = Ledger(name, message.server,
                                                  message.author.name,
                                                  message.author.id,
                                                  "%sStoreKey" %
                                                  message.author.id)
                da_books[message.server].load_save()
                da_books[message.server].load_config()
                await client.send_message(message.channel,
                                      'Ledger Loaded.')
        elif not da_books.get(message.server, False):
            await client.send_message(message.channel,
                                      'No Ledger on this server.')
        elif command == 'Save':
            da_books[message.server].save()
            await client.send_message(message.channel,
                                      'Ledger Saved.')
        elif command == 'Show Items':
            await client.send_message(message.channel,
                                      da_books[message.server].item_list())
        elif command == 'Total Value':
            await client.send_message(
                message.channel,
                da_books[message.server].total_value()[3]
            )
        elif command == 'Rectify':
            await client.send_message(
                message.channel,
                da_books[message.server].show_rectify()
            )
        elif command.startswith('Add Account '):
            account = message.content[3:].lstrip('Add Account').split(' ')[0]
            await client.send_message(
                message.channel,
                da_books[message.server].add_user(message.author.name, account,
                                                  message.author.id)[1]
            )
            da_books[message.server].save()
        elif command.startswith('Show Accounts'):
            await client.send_message(
                message.channel,
                da_books[message.server].show_users()
            )
        elif command.startswith('Show History'):
            if 'Show History' == command:
                await client.send_message(
                    message.channel,
                    da_books[message.server].transaction_log()
                )
            else:
                await client.send_message(
                    message.channel,
                    da_books[message.server].transaction_log(
                        int(command.lstrip('Show History '))
                    )
                )
        elif command.startswith('New Item '):
            data = command.lstrip("New Item ")
            item, value = data.split(':')
            item = item.strip()
            value = float(value.strip())
            mess = ''
            if da_books[message.server].admin_new_item(
                    message.author.id, item, value):
                mess += 'Successfully Added %s.\n' % item
                da_books[message.server].save()
            else:
                mess += 'Item could not be added.\n'
            await client.send_message(
                message.channel,
                mess
            )
        elif command.startswith('Set Value '):
            await client.send_message(
                message.channel,
                da_books[message.server].transaction(command,
                                                     message.author.id)
            )
            da_books[message.server].save()
        elif command.startswith('Delete Item '):
            item = command.lstrip('Delete Item ')
            mess = ''
            if da_books[message.server].delete_item(item, message.author.id):
                mess += 'Item Successfully deleted.\n'
                da_books[message.server].save()
            else:
                mess += 'Item could not be deleted.\n'
            await client.send_message(
                message.channel,
                mess
            )
        elif da_books[message.server].is_account_name(command.split()[0]):
            if command.split()[1] == 'Balance':
                await client.send_message(
                    message.channel,
                    da_books[message.server].show_balance(command.split()[0])[3]
                )
            else:
                res = da_books[message.server].transaction(command,
                                                           message.author.id)
                if res:
                    await client.send_message(
                        message.channel,
                        res
                    )
                else:
                    await client.send_message(
                        message.channel,
                        'Transaction Complete.'
                    )
                    da_books[message.server].save()
    elif message.content.startswith('Create Vote'):
        if message.content.split("ID:")[1].split("Q:")[0].strip() in votes.votes:  # id
            await client.send_message(message.channel, "Vote already exists. To Overwrite, delete previous first.")
        else:
            try:
                new_vote = votes.create_vote(message.content[11:])
                await client.send_message(message.channel, "Vote %s created" % new_vote)
            except IndexError as e:
                await client.send_message(message.channel, "You didn't put in the vote right. Try again.")
    elif message.content.startswith('Save Votes'):
        votes.save_votes()
        await client.send_message(message.channel, "Votes saved to file.")
    elif message.content.startswith('Load Votes'):
        votes.load_votes()
        await client.send_message(message.channel, 'Votes Loaded')
    elif message.content.startswith('Delete Vote:'):
        votes.votes.pop(message.content[len('Delete Vote:'):])
        await client.send_message(message.channel, 'Deleted '
                                  + message.content[len('Delete Vote:'):])
    elif message.content.startswith('Vote:'):
        try:
            result = votes.add_votes(message.content[len('Vote:'):],
                                     message.author.id)
            await client.send_message(message.channel, result)
        except:
            await client.send_message(message.channel, 'Please double check your vote, something seems to have gone wrong.')
    elif message.content.startswith('Show Vote:'):
        try:
            result = votes.show_vote(message.content[len('Show Vote:'):].strip())
            await client.send_message(message.channel, result)
        except KeyError:
            await client.send_message(message.channel,
                                      'Vote ID does not exist.')
    elif message.content.startswith('Show Vote IDs'):
        await client.send_message(message.channel, votes.IDs())
    elif message.content.startswith('Request:'):
        with open('request_File.txt', 'a') as f:
            output = '%s: %s\n' % (message.author.name,
                                   message.content[len('Request:'):].strip())
            f.write(output)
        await client.send_message(message.channel, "Thank you for the Request.")
    elif '<@{}>'.format(client.user.id) in sp or client.user.name in sp:
        await client.send_message(message.channel, 'You mentioned me, what do you want.')


client.run('MzUxNzk0ODE1MzM3MzY1NTA0.DIYqlQ.UVrBAuEhmv-N3vQyKlg9s0wkDk4')
