import asyncio
import telegram
import httpx
import json

TOKEN = "7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4"
DEFAULT_CHAT_ID = '7244291557'  # Default chat_id if no recent messages

URL_TELEGRAM_BASE = f'https://api.telegram.org/bot{TOKEN}'
URL_GET_UPDATES = f'{URL_TELEGRAM_BASE}/getUpdates'

bot = telegram.Bot(token=TOKEN)

async def send_message(text, chat_id):
    # Send async message using the bot
    await bot.send_message(chat_id=chat_id, text=text)

async def fetch_updates():
    timeout = httpx.Timeout(10.0, connect=60.0)  # Increase timeout as needed
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(URL_GET_UPDATES)
        return response

async def send_dm():
    try:
        response = await fetch_updates()

        if response.status_code == 200:
            data = response.json()

            result = data.get('result')
            processed_chat_ids = set()  # Set to store processed chat IDs

            if result:
                for res in result:
                    chat_id = res.get('message', {}).get('chat', {}).get('id', DEFAULT_CHAT_ID)

                    if chat_id not in processed_chat_ids:
                        print(f"Sending message to chat ID: {chat_id}")
                        await send_message(text='Hi! How are you? I am a bot.', chat_id=chat_id)
                        processed_chat_ids.add(chat_id)  # Mark this chat ID as processed
                    else:
                        print(f"Already sent a message to chat ID: {chat_id}")

            else:
                print(f"No new messages found. Using default chat ID: {DEFAULT_CHAT_ID}.")
                if DEFAULT_CHAT_ID not in processed_chat_ids:
                    await send_message(text='Hi! How are you? I am a bot.', chat_id=DEFAULT_CHAT_ID)
                    processed_chat_ids.add(DEFAULT_CHAT_ID)
                else:
                    print(f"Already sent a message to default chat ID: {DEFAULT_CHAT_ID}")
        else:
            print("Failed to fetch updates.")
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error occurred: {exc.response.content}")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")

if __name__ == '__main__':
    asyncio.run(send_dm())
