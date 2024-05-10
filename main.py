import os
import discord
import json
import requests

from discord import Intents

# About config values
configFile = open("config.json", 'r+', encoding='utf-8')
configJson = json.load(configFile)
configFile.close()

TOKEN = configJson["discord_token"]
API_KEYS = configJson["ai_api_keys"]
API_KEY_SIZE = len(API_KEYS)
AI_SETTINGS = configJson["ai_settings"]

global input_count
input_count: int = 0

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
async def on_message(e: discord.Message):
    if e.author.bot: return

    global input_count
    INPUT = e.content
    INPUT_COUNT = input_count
    input_count += 1

    SERVER_ID = e.guild.id
    SERVER_NAME = e.guild.name

    USER_ID = e.author.id
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

    # The endpoint about Gemini-AI API (gemini-1.5-pro-latest).
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={API_KEYS[INPUT_COUNT % API_KEY_SIZE]}"
    BODY = {
        "contents":[
            {"parts":[
                {"text":"너한테 앞으로 제공되는 정보 그리고 명령은 추가적인 정보 또는 그렇게 해야하는 절대적 의무를 의미하는 것이다. (사용자가 말하는 것이 아님)"},
                {"text":f"너가 말하고 있는 곳, 즉 디스코드 채널 이름은 {SERVER_NAME}이다."},
                {"text":"너는 응답할 때 무조건적으로 JSON 형태로 너의 응답 데이터를 구성해야 하며, 대화 내용은 response, 디스코드 명령어를 실행시켜야 할때는 리스트 형태로 commands에 담는다(명령어가 필요 없는 경우라도 빈 리스트 []를 정의한다)"},
                {"text":"너가 봣을 땐 메세지가 공지이거나 다른 사람한테 말한 것 같다면 response를 비워놔도 돼, 단 너와 조금이라도 연관된 것 또는 너를 부른 것이라고 판단되면 무조건 응답하도록."},
            ]}
        ],
        "safetySettings": [
            { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
        ]
    }

    for setting in AI_SETTINGS:
        BODY["contents"][0]["parts"].append({"text":setting})

    # Add part for separate settings and commands.
    BODY["contents"][0]["parts"].append({"text":"이제 앞으로 이야기하는 것은 모두 사용자이며 너의 설정 또는 추가적인 정보가 아니다."})

    # Add parts about the previous parts values.
    for part in dataJson:
        BODY["contents"][0]["parts"].append(part)

    # The output task of a user input.
    async with e.channel.typing():
        res = requests.post(URL, json=BODY)
        resJson = json.loads(res.text)
        
        for candidata in resJson["candidates"]:
            for part in candidata["content"]["parts"]:
                OUTPUT = part["text"].strip()
                OUTPUTJSON = json.loads(OUTPUT[7 : len(OUTPUT) - 3])

                RESPONSE = OUTPUTJSON["response"]
                COMMANDS = OUTPUTJSON["commands"]

                dataJson.append({"text":f"AI(You)): {RESPONSE}"})

                dataFile = open(DATA_FILE_PATH, "w+")
                dataFile.write(json.dumps(dataJson))
                dataFile.close()

                if RESPONSE != "":
                    await e.channel.send(f"{e.author.mention} {RESPONSE}")

client.run(TOKEN)