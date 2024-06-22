import asyncio,re,requests,json
import time

from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins

#定义信息 TG BOT
api_id = ''
api_hash = ''

user_ids = [""]  # 订阅频道或者监控用户
channel_ids = []  # 公共聊天频道 防止突然开启聊天 只监控admin



#定义信息 DBOT
chain = "solana"
number = 0.1  #购买 sol 数量

def dbot_buy(token_address,chain,number):
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
        "amountOrPercent": number,  # 购买多少sol
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

    data = response.json()
    if  data['err'] == True:
        print(data,"交易失败")
    else:
        limitPrice_sell(token_address,3.5)



def limitPrice_sell(token_address,multiple):
    #8Ey8maZF1JV6igUxVa6bv4P33cNRVFVWHmde8QaUSZeS可以替换为你的钱包 会通过API拿到你的购买成本
    time.sleep(5) #这里延迟5s 怕拿不到数据 一般没有问题
    get_price = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletstat/BPGHWxNGc41qjGbuDkwoq7z11pnBPuBVHWhAC2dSmL5i?token_address={token_address}"
    response = requests.get(get_price)

    # 解析响应的JSON数据
    data = json.loads(response.text)['data']

    if data:
        avg_cost = data["avg_cost"]

        # 输出data里的price
        if not avg_cost == 0:
            print("平均购买成本 ：", avg_cost)

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
                        "triggerPriceUsd": avg_cost * multiple, #触发买入/卖出的价格（美元）
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

            if response.json()["err"] == False :
                print("挂单成功")




#监控TG
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()  # 启动 client

    admin_ids = []
    # 对每个频道获取管理员列表
    for channel_id in channel_ids:
        admins = await client.get_participants(channel_id, filter=ChannelParticipantsAdmins())
        admin_ids.extend([admin.id for admin in admins])  # 将每个频道的管理员 ID 添加到列表中

    processed_matches = set()  # 创建一个空的集合来存储已经处理过的 token

    if user_ids:
        @client.on(events.NewMessage(from_users=user_ids))
        async def handler(event):
            print('Received message:', event.message.text)
            start_time1 = time.time()  # 记录开始时间
            print('---------------------------------------------------------------')
            pattern = r'\b(?!0x)[A-Za-z0-9]{41,}\b'
            token_addres = re.findall(pattern, event.message.text)
            for token_addr in token_addres:
                if token_addr not in processed_matches:  # 如果 match 还没有被处理过
                    print("开始购买 Ca ： ",token_addr)
                    dbot_buy(token_addr,chain,number)
                    end_time1 = time.time()  # 记录结束时间
                    print("执行时间：", end_time1 - start_time1 - 5 , "秒 ， -时间代表购买失败")  # 输出执行时间
                    print('---------------------------------------------------------------')
                    processed_matches.add(token_addr)  # 将 match 添加到已处理集合中

    if channel_ids:
        @client.on(events.NewMessage(chats=channel_ids))
        async def handler(event):
            # 判断消息是否来自于管理员
            if event.message.sender_id in admin_ids:
                print('Received message:', event.message.text)
                start_time2 = time.time()  # 记录开始时间
                print('---------------------------------------------------------------')
                pattern = r'\b(?!0x)[A-Za-z0-9]{41,}\b'
                token_addres = re.findall(pattern, event.message.text)
                for token_addr in token_addres:
                    if token_addr not in processed_matches:  # 如果 match 还没有被处理过
                        print("开始购买 Ca ： ", token_addr)
                        dbot_buy(token_addr,chain,number)
                        end_time2 = time.time()  # 记录结束时间
                        print("执行时间：", end_time2 - start_time2 - 5 , "秒 ， -时间代表购买失败")  # 输出执行时间
                        print('---------------------------------------------------------------')
                        processed_matches.add(token_addr)  # 将 match 添加到已处理集合中

    print('Listening for messages from the admins of the channel and specific users')

    await client.run_until_disconnected()  # 持续监控

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
