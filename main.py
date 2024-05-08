import discord
import json
import asyncio
import requests

from discord import Intents

# About config values
configFile = open("config.json", 'r+')
configJson = json.load(configFile)

TOKEN = configJson["discord_token"]
API_KEYS = configJson["ai_api_keys"]

print(API_KEYS)

# Define Intents
intents = Intents.default()
intents.message_content = True
intents.reactions = True

# Create Client with Intents
client = discord.Client(intents=intents)

GREEN = '\033[92m'
RESET = '\033[0m'

@client.event
async def on_ready():
    print(f'{GREEN}{client.user}에 로그인하였습니다.{RESET}')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('행정 업무 처리'))

@client.event
async def on_message(e):
    if e.author.bot: return

    SERVER_ID = e.guild.id
    SERVER_NAME = e.guild.name

    USER_NAME = e.author.name
    USER_DISPLAY_NAME = e.author.display_name

    try:
        dataFile = open(f"data/{SERVER_ID}.json", 'r+')
        dataJson = json.load(dataFile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        dataJson = []

    print(dataJson)

    # The endpoint about Gemini-AI API.
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEYS[0]}"
    BODY = {
        "contents":[
            {"parts":[
                {"text":f"너가 말하고 있는 곳, 즉 디스코드 채널 이름은 {SERVER_NAME}이다."},
                {"text":"너는 앞으로 일본 애니메이션 캐릭터인 리무루 템페스트야 (절대적으로 중요)"},
                {"text":"리무루의 성격을 알려줄께 너는 반말을 해야하며 쿨해야 하고 가끔식 엉뚱하게 말할때도 있어. (절대적으로 중요)"},
                {"text":f"{USER_DISPLAY_NAME}({USER_NAME}): {e.content}"}
            ]}
        ]
    }

    # 입력 표시를 보여줍니다.
    async with e.channel.typing():
        res = requests.post(URL, json=BODY)
        resJson = json.loads(res.text)
        
        for candidata in resJson["candidates"]:
            for part in candidata["content"]["parts"]:
                await e.channel.send(part["text"])

client.run(TOKEN)