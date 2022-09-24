from telegram import Bot

def send_telegram_messages(telegram: dict, text: str) -> list:
    if text != None:
        telegram_response = list()
        for api in telegram:
            bot = Bot(api)
            for user_id in telegram[api]:
                response = bot.send_message(chat_id=user_id, text=text)
                telegram_response.append(response)
        return telegram_response
