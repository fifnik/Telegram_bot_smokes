from aiogram import Dispatcher

from . import admin, finance, gift, inventory, leaderboard, lootbox, market, start


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(finance.router)
    dp.include_router(leaderboard.router)
    dp.include_router(inventory.router)
    dp.include_router(market.router)
    dp.include_router(lootbox.router)
    dp.include_router(gift.router)
    dp.include_router(admin.router)
