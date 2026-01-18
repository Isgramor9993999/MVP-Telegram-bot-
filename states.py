from aiogram.fsm.state import State, StatesGroup

class BuyStates(StatesGroup):
    waiting_for_payment = State()
