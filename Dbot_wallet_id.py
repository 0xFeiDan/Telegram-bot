import requests , json

url = "https://api-bot-v1.dbotx.com/account/wallets?type=solana"

headers = {"X-API-KEY": "填入你的API"}

response = requests.get(url, headers=headers)

print(json.loads(response.text)["res"])