import discord
import asyncio
import rolling
import voting
import pickle

client = discord.Client()

qwk_help = """For more specific help type help [topic].
Topics are :
- dice
- voting
- request"""

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
ID: ID value of the 
Q: Question raised or asked, try to keep it simple.
O: Options in a comma separated list.
N: Number of votes each person has. If value is greater then number of options
then 1 vote per option is allowed.

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
Show Vote: [ID]
"""

request_help = """Syntax:
Request: [Request]

This is for requesting changes or features for butter bot.

It will save them so that My Creator can act on them later.

Thank you for the request.
"""

votes = voting.voting()

@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------')

@client.event
async def on_message(message):
    mess = message.content
    sp = mess.split()
    if sp[0] == '<@{}>'.format(client.user.id):
        if len(sp) <= 1:
            await client.send_message(message.channel, 'I can\'t do that.')
        elif 'purpose' in message.content:
            await client.send_message(message.channel, 'To pass butter')
        elif 'help' == sp[1]:
            if len(sp) <= 2:
                await client.send_message(message.channel, qwk_help)
            elif sp[2] == 'dice':
                await client.send_message(message.channel, dice_help)
            elif sp[2] == 'voting':
                await client.send_message(message.channel, voting_help)
            elif sp[2] == 'request':
                await client.send_message(message.channel, request_help)
            else:
                await client.send_message(message.channel, qwk_help)
        elif 'real purpose' in message.content.lowercase():
            await client.send_message(message.channel,
                                      'To roll dice and collect votes.')
    elif '.r' == sp[0]:
        await client.send_message(message.channel, rolling.roll(sp[1:]))
    elif mess.startswith('Create Vote'):
        if mess.split("ID:")[1].split("Q:")[0].strip() in votes.votes:  # id
            await client.send_message(message.channel, "Vote already exists. To Overwrite, delete previous first.")
        else:
            try:
                new_vote = votes.create_vote(mess.lstrip("Create Vote"))
                await client.send_message(message.channel, "Vote %s created" % new_vote)
            except IndexError as e:
                await client.send_message(message.channel, "You didn't put in the vote right. Try again.")
    elif mess.startswith('Save Votes'):
        votes.save_votes()
        await client.send_message(message.channel, "Votes saved to file.")
    elif mess.startswith('Load Votes'):
        votes.load_votes()
        await client.send_message(message.channel, 'Votes Loaded')
    elif mess.startswith('Delete Vote:'):
        votes.votes.pop(mess.lstrip('Delete Vote:'))
        await client.send_message(message.channel, 'Deleted ' + mess.lstrip('Delete Vote:'))
    elif mess.startswith('Vote:'):
        try:
            result = votes.add_votes(mess.lstrip('Vote:'), message.author.id)
            await client.send_message(message.channel, result)
        except:
            await client.send_message(message.channel, 'Please double check your vote, something seems to have gone wrong.')
    elif mess.startswith('Show Vote:'):
        try:
            result = votes.show_vote(mess.lstrip('Show Vote:'))
            await client.send_message(message.channel, result)
        except KeyError:
            await client.send_message(message.channel,
                                      'Vote ID does not exist.')
    elif mess.startswith('Show Vote IDs'):
        await client.send_message(message.channel, votes.IDs())
    elif mess.startswith('Request:'):
        with open('request_File.txt', 'a') as f:
            output = '%s: %s\n' % (message.author.name,
                                   mess.lstrip('Request:').strip())
            f.write(output)
        await client.send_message(message.channel, "Thank you for the Request.")
    elif '<@{}>'.format(client.user.id) in sp or client.user.name in sp:
        await client.send_message(message.channel, 'You mentioned me, what do you want.')


client.run('MzUxNzk0ODE1MzM3MzY1NTA0.DIYqlQ.UVrBAuEhmv-N3vQyKlg9s0wkDk4')
