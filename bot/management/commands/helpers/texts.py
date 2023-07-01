MESSAGE_START = (
    'Привет, {username} \!\n'
    'Для начала игры отправь команду /game\n\n'
    '_Так же ты можешь добавить меня в групповой чат  и играть в нём\._\n\n'
    'Для просмотра своего баланса отправь /balance мне {bot_username} в личном чате\n\n'
    'Канал, где хранятся все сессии: {archive}'
)

MESSAGE_BALANCE = (
    'Игрок: {username}\n'
    'Баланс: {balance}'
)

MESSAGE_LOW_BALANCE = (
    'Игрок: {username}\n'
    'У тебя *низкий баланс*: {balance}\n\n'
    'Для пополнения баланса отправь /balance мне {bot_username} в личном чате\n\n'
    'Канал, где хранятся все сессии: {archive}'
)

MESSAGE_SESSION = (
    'Сессия: `{session_id}`\n'
    'Игрок: {username}'
)

MESSAGE_MAKE_BET = (
    'Сессия: `{session_id}`\n'
    'Игрок: {username}\n\n'
    'Выбери ставку:'
)

MESSAGE_CHOOSE_AMOUNT = (
    'Сессия: `{session_id}`\n'
    'Игрок: {username}\n\n'
    'Ставка: {amount}'
)

MESSAGE_CLOSE_SESSION = (
    'Сессия: `{session_id}`\n'
    'Игрок: {username}\n\n'
    'Ставка: {amount}\n'
    'Баланс: {balance}\n'
    'Сессия закрыта'
)

MESSAGE_MAKE_SPIN = (
    'Сессия: `{session_id}`\n'
    'Игрок: {username}\n\n'
    'Ставка: {amount}\n'
    'Выигрыш: {win}\n\n'
    'Канал, где хранятся все сессии: {archive}'
)

CALLBACK_MAKE_BET_TEXT = 'Сделать ставку'
CALLBACK_PAYTABLE_TEXT = 'Paytable'
CALLBACK_CANCEL_TEXT = 'Отмена'
CALLBACK_MAKE_SPIN_TEXT = 'Сделать спин'
CALLBACK_CLOSE_SESSION_TEXT = 'Закрыть сессию'
CALLBACK_BALANCE_TEXT = 'Баланс'
CALLBACK_TOPUP_TEXT = 'Пополнить баланс'

BET_AMOUNTS = [2, 3, 4, 5,
               6, 7, 8, 9,
               10, 20]

NOTIFY_NOT_ENOUGH_MONEY = (
    'У тебя не достаточно средств для данной ставки.\n'
    'Ставка: {amount}\n'
    'Твой баланс: {balance}'
)