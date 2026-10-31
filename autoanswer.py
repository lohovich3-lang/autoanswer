import os
from telethon import TelegramClient, events

# ----------------------------------------------------------------------
# 1. НАСТРОЙКИ (Ваши данные)
# ----------------------------------------------------------------------
API_ID = int(os.environ.get("API_ID", 0))          # Замените на ваш api_id (число)
API_HASH = os.environ.get("API_HASH", "") # Замените на ваш api_hash

# Текст фиксированного автоответа
WELCOME_MESSAGE = (
    "Приветствую! Спасибо за сообщение. 😉\n"
    "Я сейчас не в сети, но обязательно отвечу, как освобожусь!\n" 
    "(Или могу проигнорить и забыть🤐)"
)

# Инициализация клиента Telethon
client = TelegramClient("user_session", API_ID, API_HASH)

# Переключатель: включен ли автоответчик (можно выключать/включать командой /away в Избранном)
AUTO_REPLY_ENABLED = True

# Команда для включения/выключения автоответчика (писать себе в Избранное)
@client.on(events.NewMessage(pattern="/away", outgoing=True))
async def toggle_away(event):
    global AUTO_REPLY_ENABLED
    AUTO_REPLY_ENABLED = not AUTO_REPLY_ENABLED
    status = "включен ✅" if AUTO_REPLY_ENABLED else "выключен ❌"
    await event.edit(f"🤖 Автоответчик теперь {status}")

# ----------------------------------------------------------------------
# 2. ЛОГИКА АВТООТВЕТА БЕЗ НЕЙРОСЕТЕЙ
# ----------------------------------------------------------------------
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_new_message(event):
    global AUTO_REPLY_ENABLED
    
    if not AUTO_REPLY_ENABLED:
        return

    sender = await event.get_sender()
    
    # Игнорируем ботов, каналы и пустые сообщения
    if not sender or getattr(sender, 'bot', False) or not event.raw_text:
        return

    chat_id = event.chat_id

    # --- ПРОВЕРКА ИСТОРИИ ЧАТА ---
    # Проверяем последние сообщения: писали ли МЫ (вы) этому человеку раньше?
    async for message in client.iter_messages(chat_id, limit=30):
        if message.out:  # Если найдено ваше исходящее сообщение
            # Значит, вы уже общались или первыми вышли на связь — молчим
            return
    # -----------------------------

    incoming_text = event.raw_text
    print(f"[+] Новое входящее от незнакомца {sender.first_name}: {incoming_text}")

    try:
        # Отправляем фиксированный ответ собеседнику
        await event.reply(WELCOME_MESSAGE)
        print(f"[+] Успешно отправлен автоответ для {sender.first_name}")

    except Exception as e:
        print(f"[-] Ошибка при отправке автоответа: {e}")

if __name__ == "__main__":
    print("🤖 Юзербот-автоответчик успешно запущен и следит за чатами...")
    client.start()
    client.run_until_disconnected()