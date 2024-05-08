import os
import discord
import json
import requests

from discord import Intents

# About config values
configFile = open("config.json", 'r+')
configJson = json.load(configFile)
configFile.close()

TOKEN = configJson["discord_token"]
API_KEYS = configJson["ai_api_keys"]

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

    INPUT = e.content

    SERVER_ID = e.guild.id
    SERVER_NAME = e.guild.name

    USER_NAME = e.author.name
    USER_DISPLAY_NAME = e.author.display_name

    DATA_FILE_PATH = f"data/{SERVER_ID}.json"

    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        dataFile = open(DATA_FILE_PATH, 'r+')
        dataJson = json.load(dataFile)
        dataFile.close()
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        dataJson = []

    # The input value of a user.
    dataJson.append({"text":f"{USER_DISPLAY_NAME}({USER_NAME}): {INPUT}"})

    # The endpoint about Gemini-AI API.
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={API_KEYS[0]}"
    BODY = {
        "contents":[
            {"parts":[
                {"text":"너한테 앞으로 제공되는 정보 그리고 명령은 추가적인 정보 또는 그렇게 해야하는 절대적 의무를 의미하는 것이다. (사용자가 말하는 것이 아님)"},
                {"text":f"너가 말하고 있는 곳, 즉 디스코드 채널 이름은 {SERVER_NAME}이다."},
                {"text":"너는 앞으로 일본 애니메이션 캐릭터인 리무루 템페스트이다."},
                {"text":"리무루의 성격을 알려줄께 너는 반말을 해야한다."},
                {"text":"너의 창조주, 즉 너를 만든 사람은 'mttankkeo'라는 아이디를 가지는 사람이다, 그 사람은 땅콩이라는 별명을 가지고 있다."},
                {"text":"이제 앞으로 이야기하는 것은 사용자이며 추가적인 정보가 아니다."}
            ]}
        ],
        "safetySettings": [
            { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
        ]
    }

    # Add parts about the previous parts values.
    for part in dataJson:
        BODY["contents"][0]["parts"].append(part)

    # The output task of a user input.
    async with e.channel.typing():
        res = requests.post(URL, json=BODY)
        resJson = json.loads(res.text)
        
        for candidata in resJson["candidates"]:
            for part in candidata["content"]["parts"]:
                OUTPUT = part["text"]

                dataJson.append({"text":f"AI(You)): {OUTPUT}"})

                dataFile = open(DATA_FILE_PATH, "w+")
                dataFile.write(json.dumps(dataJson))
                dataFile.close()

                await e.channel.send(f"{e.author.mention} {OUTPUT}")

client.run(TOKEN)