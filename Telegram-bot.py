import asyncio,re,requests,json
import time

from telethon import TelegramClient, events


#定义信息 TG BOT
api_id = ''
api_hash = ''
username1 = '' #监控TG用户名
username2 = 'yingheTWbot' #监控TG 用户名

#定义信息 DBOT
chain = "solana"

def dbot_buy(token_address,chain):
    url = "https://api-bot-v1.dbotx.com/automation/swap_order"

    # 你的API密钥
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": ""  #DBOT API
    }

    data = {
        "chain": chain,  # 链条
        "pair": token_address,  # token地址
        "walletId": "",  # 钱包id
        "type": "buy",  # 买
        "amountOrPercent": 1,  # 购买多少sol
        "priorityFee": 0.005,  # gas费
        "gasFeeDelta": "",  # 额外增加的gas (Gwei)，对EVM链有效
        "maxFeePerGas": "",  # 愿意支付的最大gas (Gwei)，对EVM链有效
        "jitoEnabled": False,  # 是否防夹
        "jitoTip": "",  # 贿赂费用
        "maxSlippage": 0.25,  # 最大滑点（0.00-1.00）
        "concurrentNodes": 3,  # 并发节点数（1-3）
        "retries": 10  # 失败后的重试次数（0-10）
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.json())
    data = response.json()
    if data:
        limitPrice_sell(token_address,3.5)  #设置挂单 3.5是成本的倍数



def limitPrice_sell(token_address,multiple):

    #8Ey8maZF1JV6igUxVa6bv4P33cNRVFVWHmde8QaUSZeS可以替换为你的钱包 会通过API拿到你的购买成本

    get_price = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletstat/BPGHWxNGc41qjGbuDkwoq7z11pnBPuBVHWhAC2dSmL5i?token_address={token_address}"
    response = requests.get(get_price)

    # 解析响应的JSON数据
    data = json.loads(response.text)['data']['avg_cost']

    # 输出data里的price
    print("平均购买成本 ：",data)

    url = "https://api-bot-v1.dbotx.com/automation/limit_orders"

    # 你的API密钥
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": "" #DBOT API
    }

    data = {
        "chain": "solana",
        "pair": token_address,
        "walletId": "", #钱包ID
        "settings": [
            {
                "enabled": True,
                "tradeType": "sell",
                "triggerPriceUsd": data * multiple, #触发买入/卖出的价格（美元）
                "triggerDirection": "up",
                "priorityFee": "0.005", #优先费用 (SOL)，对Solana有效，空字符串表示使用自动优先费
                "currencyAmountUI": 0.5, #交易类型为buy时，填写买入金额（ETH/SOL/BNB），交易类型为sell时，填写卖出比例（0.00-1.00）
                "gasFeeDelta": "",  # 额外增加的gas (Gwei)，对EVM链有效
                "maxFeePerGas": "", #愿意支付的最大gas (Gwei)，对EVM链有效
                "jitoEnabled": False,
                "jitoTip": "",
                "expireDelta": 360000000, #过期时间
                "maxSlippage": 0.3,# 最大滑点（0.00-1.00）
                "concurrentNodes": 3, # 并发节点数（1-3）
                "retries": 10 # 失败后的重试次数（0-10）
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.json(),"限价订单挂单成功")

#监控TG
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # 假设 username1 和 username2 是你想要监控的两个用户
    processed_matches = set()  # 创建一个空的集合来存储已经处理过的 match
    @client.on(events.NewMessage(from_users=[username1, username2]))
    async def handler(event):
        start_time = time.time()  # 记录开始时间
        print('Received message:', event.message.text)
        print('---------------------------------------------------------------')
        pattern = r'[A-Za-z0-9]{40,}'
        matches = re.findall(pattern, event.message.text)
        for match in matches:
            if match not in processed_matches:  # 如果 match 还没有被处理过
                print(match)
                dbot_buy(match,chain)
                end_time = time.time()  # 记录结束时间
                print("执行时间：", end_time - start_time, "秒")  # 输出执行时间
                processed_matches.add(match)  # 将 match 添加到已处理集合中
    await client.start()

    print('Listening for messages from', username1, 'and', username2)

    await client.run_until_disconnected()  # 持续监控

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


