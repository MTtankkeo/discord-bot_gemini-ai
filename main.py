import discord
import json
from discord import Intents

# About config values
configFile = open("config.json", 'r')
configJson = json.load(configFile)

Token = configJson["discord_token"]

# Define Intents
intents = Intents.default()
intents.message_content = True
intents.reactions = True

# Create Client with Intents
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Login...')
    print(f'{client.user}에 로그인하였습니다.')
    print(f'ID: {client.user.name}')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('행정 업무 처리'))

@client.event
async def on_message(e):
    if e.author.bot: return

    await e.channel.send("나는냐 뽀로로 티아노 사우르스")
    print(e.author)

client.run(Token)