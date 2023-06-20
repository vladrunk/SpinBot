from telebot import TeleBot
from telebot.types import (
    Message,
    CallbackQuery,
    User,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from SpinBot.settings import (
    BOT_TOKEN,
    INIT_BALANCE, ARCHIVE_CHANNEL_ID, DEBUG,
)
from .helpers.callbacks_data import (
    CALLBACK_BALANCE_DATA,
    CALLBACK_BALANCE_NAME,
    CALLBACK_MAKEBET_DATA,
    CALLBACK_MAKEBET_NAME,
    CALLBACK_PAYTABLE_DATA,
    CALLBACK_CHOOSEAMOUNT_DATA,
    CALLBACK_CHOOSEAMOUNT_NAME,
    CALLBACK_CANCELBET_DATA,
    CALLBACK_CANCELBET_NAME,
    CALLBACK_MAKESPIN_DATA,
    CALLBACK_MAKESPIN_NAME, CALLBACK_TOPUP_DATA, CALLBACK_TOPUP_NAME,
)
from .helpers.texts import (
    MESSAGE_START,
    MESSAGE_BALANCE,
    MESSAGE_MAKE_BET,
    BET_AMOUNTS,
    MESSAGE_LOW_BALANCE,
    MESSAGE_SESSION,
    CALLBACK_BALANCE_TEXT,
    CALLBACK_MAKE_BET_TEXT,
    CALLBACK_PAYTABLE_TEXT,
    CALLBACK_CANCEL_TEXT,
    MESSAGE_CHOOSE_AMOUNT,
    CALLBACK_MAKE_SPIN_TEXT,
    MESSAGE_MAKE_SPIN,
    NOTIFY_NOT_ENOUGH_MONEY,
    CALLBACK_TOPUP_TEXT, MESSAGE_CLOSE_SESSION,
)
from time import sleep
from .models import (
    Users,
    Sessions,
    CallbackMakeBet,
    CallbackChooseAmount,
    CallbackCancelBet,
    CallbackMakeSpin,
    Combinations,
)


def update_listener(us):
    for u in us:
        print(u)


class Bot:
    def __init__(self):
        self.__bot = TeleBot(token=BOT_TOKEN)
        if DEBUG:
            self.__bot.set_update_listener(update_listener)
        self.__bot_username = self.__get_username(user=self.__bot.get_me())
        self.__archive = self.__bot.get_chat(chat_id=ARCHIVE_CHANNEL_ID)
        self.__archive_username = f'@{self.__archive.username}'.replace('_', '\_')
        self.running = False

    @staticmethod
    def __markup_show_balance(user_id: int):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                text=CALLBACK_BALANCE_TEXT,
                callback_data=CALLBACK_BALANCE_DATA.format(user_id=user_id)
            ),
        )
        return markup

    @staticmethod
    def __markup_topup(user_id: int):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                text=CALLBACK_TOPUP_TEXT,
                callback_data=CALLBACK_TOPUP_DATA.format(user_id=user_id)
            ),
        )
        return markup

    @staticmethod
    def __markup_make_bet(session: Sessions):
        cb, _ = CallbackMakeBet.objects.get_or_create(session=session)

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton(
                text=CALLBACK_MAKE_BET_TEXT,
                callback_data=CALLBACK_MAKEBET_DATA.format(callback_id=cb.id)
            ),
            InlineKeyboardButton(
                text=CALLBACK_PAYTABLE_TEXT,
                callback_data=CALLBACK_PAYTABLE_DATA
            ),
            row_width=1,
        )

        return markup

    @staticmethod
    def __markup_choose_amount(session: Sessions):
        markup = InlineKeyboardMarkup()

        buttons = []

        for amount in BET_AMOUNTS:
            cb, _ = CallbackChooseAmount.objects.get_or_create(session=session, amount=amount)
            btn = InlineKeyboardButton(
                text=amount,
                callback_data=CALLBACK_CHOOSEAMOUNT_DATA.format(callback_id=cb.id)
            )
            buttons.append(btn)

        markup.add(*buttons[:-2], row_width=4)
        markup.add(*buttons[-2:], row_width=2)

        cb, _ = CallbackCancelBet.objects.get_or_create(session=session)
        markup.add(
            InlineKeyboardButton(
                text=CALLBACK_CANCEL_TEXT,
                callback_data=CALLBACK_CANCELBET_DATA.format(callback_id=cb.id)
            )
        )

        return markup

    @staticmethod
    def __markup_make_spin(session: Sessions):
        cb, _ = CallbackMakeSpin.objects.get_or_create(session=session)

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton(
                text=CALLBACK_MAKE_SPIN_TEXT,
                callback_data=CALLBACK_MAKESPIN_DATA.format(callback_id=cb.id)
            ),
            InlineKeyboardButton(
                text=CALLBACK_PAYTABLE_TEXT,
                callback_data=CALLBACK_PAYTABLE_DATA
            ),
            row_width=1,
        )

        return markup

    @staticmethod
    def __get_or_create_user(user: User) -> Users:
        try:
            return Users.objects.get(id=user.id)
        except Users.DoesNotExist:
            return Users.objects.create(id=user.id, balance=INIT_BALANCE, )

    @staticmethod
    def __get_username(user: User) -> str:
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        username = f'@{user.username}' if user.username else user.full_name
        for char in chars:
            username = username.replace(char, f'\\{char}')
        return username

    @staticmethod
    def __parse_cb_data(callback: CallbackQuery):
        _, _id = callback.data.split('#')
        return _id

    def __callback_balance(self, callback: CallbackQuery):
        # парсим ид юзера из кнопки
        _, uid = callback.data.split('#')

        try:
            # получаем игрока из БД
            user = Users.objects.get(id=int(uid))
        except Users.DoesNotExist as e:
            # если игрока нет, просто игнорим
            print(e)
            return

        if callback.from_user.id != user.id:
            # если не тот юзер нажал кнопку
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=f'Это не твоя кнопка',
            )
            return

        # начинаем отправку баланса
        text = MESSAGE_BALANCE.format(
            username=self.__get_username(user=callback.from_user), balance=user.balance,
        ).replace('.', '\.')

        self.__bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            parse_mode='MarkdownV2',
            disable_notification=True,
            reply_markup=self.__markup_topup(user_id=user.id),
        )

    def __callback_topup(self, callback: CallbackQuery):
        # парсим ид юзера из кнопки
        uid = self.__parse_cb_data(callback=callback)

        try:
            # получаем игрока из БД
            user = Users.objects.get(id=int(uid))
        except Users.DoesNotExist as e:
            # если игрока нет, просто игнорим
            print(e)
            return

        if callback.from_user.id != user.id:
            # если не тот юзер нажал кнопку
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=f'Это не твоя кнопка',
            )
            return

        user.balance += 200
        user.save()

        text = MESSAGE_BALANCE.format(
            username=self.__get_username(user=callback.from_user), balance=user.balance,
        ).replace('.', '\.')

        self.__bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=text,
            parse_mode='MarkdownV2',
            reply_markup=None,
        )

    def __callback_makebet(self, callback: CallbackQuery):
        # парсим ид колбека
        cid = self.__parse_cb_data(callback=callback)

        try:
            # получаем колбек из БД
            c = CallbackMakeBet.objects.get(id=cid)
        except CallbackMakeBet.DoesNotExist as e:
            # если колбека нет, просто игнорим
            print(e)
            return

        if callback.from_user.id != c.session.user.id:
            # если не тот юзер нажал кнопку
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=f'Это не твоя кнопка',
            )
            return

        # начинаем отправку вариантов ставок
        username = self.__get_username(user=callback.from_user)
        text = MESSAGE_MAKE_BET.format(session_id=c.session.id, username=username)

        self.__bot.edit_message_text(
            chat_id=c.session.chat_id,
            message_id=c.session.msg_id,
            text=text,
            parse_mode='MarkdownV2',
            reply_markup=self.__markup_choose_amount(session=c.session)
        )

    def __callback_cancelbet(self, callback: CallbackQuery):
        # парсим ид колбека
        cid = self.__parse_cb_data(callback=callback)

        try:
            # получаем колбек из БД
            c = CallbackCancelBet.objects.get(id=cid)
        except CallbackCancelBet.DoesNotExist as e:
            # если колбека нет, просто игнорим
            print(e)
            return

        if callback.from_user.id != c.session.user.id:
            # если не тот юзер нажал кнопку
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=f'Это не твоя кнопка',
            )
            return

        # отменяем выбор ставки
        username = self.__get_username(user=callback.from_user)
        text = MESSAGE_SESSION.format(session_id=c.session.id, username=username)

        self.__bot.edit_message_text(
            chat_id=c.session.chat_id,
            message_id=c.session.msg_id,
            text=text,
            parse_mode='MarkdownV2',
            reply_markup=self.__markup_make_bet(session=c.session)
        )

    def __callback_chooseamount(self, callback: CallbackQuery):
        # парсим ид колбека
        cid = self.__parse_cb_data(callback=callback)

        try:
            # получаем колбек из БД
            c = CallbackChooseAmount.objects.get(id=cid)
        except CallbackChooseAmount.DoesNotExist as e:
            # если колбека нет, просто игнорим
            print(e)
            return

        if callback.from_user.id != c.session.user.id:
            # если не тот юзер нажал кнопку
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=f'Это не твоя кнопка',
            )
            return

        if c.amount > c.session.user.balance:
            # если не хватает деняг
            text = NOTIFY_NOT_ENOUGH_MONEY.format(amount=c.amount, balance=c.session.user.balance)
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=text,
                show_alert=True,
            )
            return

        username = self.__get_username(user=callback.from_user)
        text = MESSAGE_CHOOSE_AMOUNT.format(session_id=c.session.id, username=username, amount=c.amount)

        self.__bot.edit_message_text(
            chat_id=c.session.chat_id,
            message_id=c.session.msg_id,
            text=text,
            parse_mode='MarkdownV2',
            reply_markup=self.__markup_make_spin(session=c.session)
        )

        c.session.amount = c.amount
        c.session.save()

    def __callback_makespin(self, callback: CallbackQuery):
        # парсим ид колбека
        cid = self.__parse_cb_data(callback=callback)

        try:
            # получаем колбек из БД
            c = CallbackMakeSpin.objects.get(id=cid)
        except CallbackMakeSpin.DoesNotExist as e:
            # если колбека нет, просто игнорим
            print(e)
            return

        if callback.from_user.id != c.session.user.id:
            # если не тот юзер нажал кнопку
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=f'Это не твоя кнопка',
            )
            return

        username = self.__get_username(user=callback.from_user)

        if c.session.amount > c.session.user.balance:
            # если не хватает деняг
            text = NOTIFY_NOT_ENOUGH_MONEY.format(amount=c.session.amount, balance=c.session.user.balance)
            self.__bot.answer_callback_query(
                callback_query_id=callback.id,
                text=text,
                show_alert=True,
            )
            text = MESSAGE_CLOSE_SESSION.format(
                session_id=c.session.id, username=username, amount=c.session.amount, balance=c.session.user.balance
            ).replace('.', '\.')
            self.__bot.edit_message_text(
                chat_id=c.session.chat_id,
                message_id=c.session.msg_id,
                text=text,
                parse_mode='MarkdownV2',
                reply_markup=None,
            )
            c.session.close = True
            c.session.save()
            self.__bot.forward_message(
                chat_id=ARCHIVE_CHANNEL_ID,
                from_chat_id=c.session.chat_id,
                message_id=c.session.msg_id,
                disable_notification=True,
            )
            return

        # начинаем отправку бандита
        message_dice = self.__bot.send_dice(
            chat_id=c.session.chat_id,
            emoji='🎰',
            disable_notification=True,
        )

        comb = Combinations.objects.get(id=message_dice.dice.value)
        win = c.session.amount * comb.mult
        text = MESSAGE_MAKE_SPIN.format(
            session_id=c.session.id, username=username, amount=c.session.amount, win=win,
            archive=self.__archive_username,
        )
        text = text.replace('.', '\.')
        self.__bot.edit_message_text(
            chat_id=c.session.chat_id,
            message_id=c.session.msg_id,
            text=text,
            parse_mode='MarkdownV2',
            reply_markup=None
        )
        c.session.user.balance += win - c.session.amount
        c.session.user.save()
        c.session.win = win
        c.session.result = comb
        c.session.close = True
        c.session.save()
        self.__bot.forward_message(
            chat_id=ARCHIVE_CHANNEL_ID,
            from_chat_id=c.session.chat_id,
            message_id=c.session.msg_id,
            disable_notification=True,
        )
        self.__bot.forward_message(
            chat_id=ARCHIVE_CHANNEL_ID,
            from_chat_id=c.session.chat_id,
            message_id=message_dice.message_id,
            disable_notification=True,
        )

    def __cmd_start(self, message: Message):
        self.__get_or_create_user(message.from_user)
        text = MESSAGE_START.format(
            username=self.__get_username(user=message.from_user), bot_username=self.__bot_username,
            archive=self.__archive_username,
        )
        self.__bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='MarkdownV2',
            disable_notification=True,
            reply_markup=self.__markup_show_balance(user_id=message.from_user.id),
        )

    def __cmd_balance(self, message: Message):
        user = self.__get_or_create_user(message.from_user)
        text = MESSAGE_BALANCE.format(
            username=self.__get_username(user=message.from_user), balance=user.balance,
        ).replace('.', '\.')

        self.__bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='MarkdownV2',
            disable_notification=True,
            reply_markup=self.__markup_topup(user_id=user.id),
        )

    def __cmd_game(self, message: Message):
        user = self.__get_or_create_user(message.from_user)
        username = self.__get_username(user=message.from_user)

        if user.balance < min(BET_AMOUNTS):
            text = MESSAGE_LOW_BALANCE.format(
                username=username, balance=user.balance, bot_username=self.__bot_username,
                archive=self.__archive_username,
            ).replace('.', '\.')

            self.__bot.send_message(
                chat_id=message.chat.id,
                text=text,
                parse_mode='MarkdownV2',
                disable_notification=True,
            )
            return

        session = Sessions.objects.create(chat_id=message.chat.id, user=user)

        text = MESSAGE_SESSION.format(username=username, session_id=session.id, )

        message_session = self.__bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='MarkdownV2',
            disable_notification=True,
            reply_markup=self.__markup_make_bet(session)
        )

        session.msg_id = message_session.message_id
        session.save()

    def __main(self):

        @self.__bot.callback_query_handler(func=lambda callback: callback.data.startswith(CALLBACK_TOPUP_NAME))
        def handler_callback_topup(callback: CallbackQuery):
            self.__callback_topup(callback=callback)

        @self.__bot.callback_query_handler(func=lambda callback: callback.data.startswith(CALLBACK_MAKESPIN_NAME))
        def handler_callback_makespin(callback: CallbackQuery):
            self.__callback_makespin(callback=callback)

        @self.__bot.callback_query_handler(func=lambda callback: callback.data.startswith(CALLBACK_CHOOSEAMOUNT_NAME))
        def handler_callback_chooseamount(callback: CallbackQuery):
            self.__callback_chooseamount(callback=callback)

        @self.__bot.callback_query_handler(func=lambda callback: callback.data.startswith(CALLBACK_CANCELBET_NAME))
        def handler_callback_cancelbet(callback: CallbackQuery):
            self.__callback_cancelbet(callback=callback)

        @self.__bot.callback_query_handler(func=lambda callback: callback.data.startswith(CALLBACK_MAKEBET_NAME))
        def handler_callback_makebet(callback: CallbackQuery):
            self.__callback_makebet(callback=callback)

        @self.__bot.callback_query_handler(func=lambda callback: callback.data.startswith(CALLBACK_BALANCE_NAME))
        def handler_callback_balance(callback: CallbackQuery):
            self.__callback_balance(callback=callback)

        @self.__bot.message_handler(commands=['start'], chat_types=['private'])
        def handler_cmd_start(message: Message):
            self.__cmd_start(message)

        @self.__bot.message_handler(commands=['balance'], chat_types=['private'])
        def handler_cmd_balance(message: Message):
            self.__cmd_balance(message)

        @self.__bot.message_handler(commands=['game'])
        def handler_cmd_game(message: Message):
            self.__cmd_game(message)

        while self.running:
            try:
                self.__bot.polling()
            except Exception as e:
                print(e)
                sleep(5)

    def start(self):
        self.running = True
        self.__main()

    def stop(self):
        self.running = False
        self.__bot.stop_polling()


bot = Bot()
