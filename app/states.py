from aiogram.fsm.state import State, StatesGroup


class TopUp(StatesGroup):
    waiting_for_amount = State()


class SellSmoke(StatesGroup):
    waiting_for_price = State()


class ChangeDescription(StatesGroup):
    waiting_for_text = State()


class GiftSmoke(StatesGroup):
    waiting_for_username = State()
    waiting_for_smoke = State()
