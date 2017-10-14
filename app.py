import discord
import asyncio

client = discord.Client()

@client.event
async def on_ready():
    print('logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------')

@client.event
async def on_message(message):
    mess = message.content
    print(mess)
    sp = mess.split()
    if sp[0] == '<@{}>'.format(client.user.id):
        if 'purpose' in message.content:
            await client.send_message(message.channel, 'To pass butter')
    #if '<@{}>'.format(client.user.id) in sp or client.user.name in sp:
    #    await client.send_message(message.channel, 'You mentioned me, what do you want.')
    print(message.mentions)


client.run('MzUxNzk0ODE1MzM3MzY1NTA0.DIYqlQ.UVrBAuEhmv-N3vQyKlg9s0wkDk4')
