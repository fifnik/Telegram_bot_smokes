from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..config import settings
from ..services.smokes import get_smoke_with_owner
from ..services.users import (
    get_all_user_ids,
    get_broadcast_logs,
    log_broadcast,
    set_balance_by_username,
)

router = Router()


def _is_owner(user_id: int) -> bool:
    return user_id == settings.owner_id


@router.message(Command("broadcast"))
async def command_broadcast(message: Message) -> None:
    if not _is_owner(message.from_user.id):
        await message.answer("⛔ У вас нет прав.")
        return
    text = message.text.removeprefix("/broadcast").strip()
    if not text:
        await message.answer("Использование: /broadcast <текст>")
        return
    sent = 0
    for user_id in get_all_user_ids():
        try:
            await message.bot.send_message(user_id, f"📢 Объявление:\n\n{text}")
            sent += 1
        except Exception:  # pragma: no cover - network errors
            continue
    log_broadcast(text, sent)
    await message.answer(f"Отправлено {sent} пользователям.")


@router.message(Command("broadcast_logs"))
async def command_broadcast_logs(message: Message) -> None:
    if not _is_owner(message.from_user.id):
        await message.answer("⛔ У вас нет прав.")
        return
    logs = get_broadcast_logs(10)
    if not logs:
        await message.answer("Логи пусты.")
        return
    lines = ["📜 Последние рассылки:\n"]
    for text, sent, timestamp_value in logs:
        date = datetime.fromtimestamp(timestamp_value).strftime("%d.%m.%Y %H:%M")
        preview = (text[:60] + "...") if len(text) > 60 else text
        lines.append(f"🗓 {date}\n👥 Отправлено: {sent}\n💬 {preview}\n")
    await message.answer("\n".join(lines))


@router.message(Command("get_score"))
async def command_get_score(message: Message) -> None:
    if not _is_owner(message.from_user.id):
        await message.answer("⛔ У вас нет прав.")
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /get_score <username> <сумма>")
        return
    username, balance_str = parts[1], parts[2]
    try:
        new_balance = int(balance_str)
    except ValueError:
        await message.answer("Баланс должен быть числом.")
        return
    if new_balance < 0:
        await message.answer("Баланс >= 0.")
        return
    if set_balance_by_username(username, new_balance):
        await message.answer(f"Баланс @{username} установлен в {new_balance}.")
    else:
        await message.answer(f"Пользователь @{username} не найден.")


@router.message(Command("smokes"))
async def command_smokes_info(message: Message) -> None:
    if not _is_owner(message.from_user.id):
        await message.answer("⛔️ У тебя нет прав для этой команды.")
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Использование: <b>/smokes [id]</b>", parse_mode="HTML")
        return
    smoke_id = int(parts[1])
    smoke = get_smoke_with_owner(smoke_id)
    if not smoke:
        await message.answer(f"❌ Сигара с ID {smoke_id} не найдена.")
        return
    sid, name, description, owner_id, is_for_sale, owner_username, price = smoke
    owner_info = f"@{owner_username}" if owner_username else f"ID: {owner_id}"
    price_text = f"\n💵 Цена: {price}" if price is not None else ""
    text = (
        f"🚬 <b>{name}</b>\n"
        f"🆔 ID: {sid}\n"
        f"📝 Описание: {description}\n"
        f"👤 Владелец: {owner_info}{price_text}\n"
    )
    await message.answer(text, parse_mode="HTML")
