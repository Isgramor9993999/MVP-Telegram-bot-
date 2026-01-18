from handlers.menu import register_menu_handlers
from handlers.trial import register_trial_handlers
from handlers.buy import register_buy_handlers
from handlers.payments import register_payment_handlers

def register_all_handlers(dp):
    register_menu_handlers(dp)
    register_trial_handlers(dp)
    register_buy_handlers(dp)
    register_payment_handlers(dp)
