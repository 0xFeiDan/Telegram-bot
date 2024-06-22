from telethon.sync import TelegramClient

# 你的 Telegram API ID 和 hash
api_id = 'your_api_id'
api_hash = 'your_api_hash'

# 创建一个 Telegram 客户端实例
with TelegramClient('session_name', api_id, api_hash) as client:
    # 获取所有对话
    dialogs = client.get_dialogs()

    for dialog in dialogs:
        # 检查对话是否是频道
        if dialog.is_channel:
            # 打印频道的 ID 和名称
            print(f"ID: {dialog.id}, Name: {dialog.name}")
