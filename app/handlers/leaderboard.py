from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..services.users import get_top_users, get_user_rank

router = Router()


@router.callback_query(F.data == "leaders")
async def callback_leaders(callback: CallbackQuery) -> None:
    await callback.answer()
    top = get_top_users(3)
    if not top:
        await callback.message.edit_text("📭 Таблица лидеров пуста.")
        return
    text_lines = ["🏆 Топ-3 игроков:", ""]
    medals = ["🥇", "🥈", "🥉"]
    for index, (user_id, username, balance) in enumerate(top):
        medal = medals[index] if index < len(medals) else "•"
        name = f"@{username}" if username else "Без ника"
        text_lines.append(f"{medal} {name} — {balance}")
    rank, balance = get_user_rank(callback.from_user.id)
    if rank and rank > 3:
        text_lines.append("")
        text_lines.append(f"➡️ Ваше место: {rank} (баланс: {balance})")
    await callback.message.edit_text("\n".join(text_lines))
