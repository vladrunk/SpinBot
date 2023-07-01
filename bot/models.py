from django.db import models
from nanoid import generate
from string import (
    ascii_lowercase,
    digits
)


def gen_id() -> str:
    return generate(''.join([ascii_lowercase, digits]), 22)


class Users(models.Model):
    id = models.IntegerField(
        primary_key=True,
        default=0,
        verbose_name='User ID',
        help_text='ID игрока из Telegram',
    )
    balance = models.FloatField(
        default=0.00,
        verbose_name='Balance',
        help_text='Баланс игрока',
    )

    def __str__(self):
        return f'User: {self.id}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Combinations(models.Model):
    id = models.IntegerField(
        primary_key=True,
        default=0,
        verbose_name='Combination ID',
        help_text='ID комбинации из Telegram',
    )
    comb = models.CharField(
        default='',
        max_length=255,
        verbose_name='Combination',
        help_text='Описание комбинации',
    )
    mult = models.FloatField(
        default=0.00,
        verbose_name='Multiply',
        help_text='Множитель ставки',
    )

    def __str__(self):
        return f'ID: {self.id} Combination: "{self.comb}"'

    class Meta:
        verbose_name = 'Combination'
        verbose_name_plural = 'Combinations'


class Sessions(models.Model):
    id = models.CharField(
        primary_key=True,
        default=gen_id,
        max_length=22,
        verbose_name='Session ID',
        help_text='ID сессии',
        editable=False,
    )
    chat_id = models.IntegerField(
        default=0,
        verbose_name='Chat ID',
        help_text='ID чата в котором созданна сессия',
    )
    thread_id = models.IntegerField(
        default=0,
        verbose_name='Thread ID',
        help_text='ID темы в которой созданна сессия',
        null=True,
    )
    user = models.ForeignKey(
        to=Users,
        on_delete=models.CASCADE,
        related_name='user',
        related_query_name='users',
        verbose_name='User',
        help_text='Игрок, который создал сессию',
    )
    msg_id = models.IntegerField(
        default=0,
        verbose_name='Message ID',
        help_text='ID сообщения с сессией',
        editable=True,
    )
    amount = models.IntegerField(
        default=0,
        verbose_name='Amount',
        help_text='Сумма ставки',
    )
    result = models.ForeignKey(
        to=Combinations,
        on_delete=models.CASCADE,
        related_name='result',
        related_query_name='results',
        verbose_name='Result',
        help_text='Результат сессии, то что выпало на барабанах',
        null=True,
    )
    win = models.IntegerField(
        default=0,
        verbose_name='Win',
        help_text='Сумма выигрыша',
    )
    close = models.BooleanField(
        default=False,
        verbose_name='Close',
        help_text='Статус сессии',
    )

    def __str__(self):
        return f'Session: {self.id}'

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'


class Callback(models.Model):
    id = models.CharField(
        primary_key=True,
        default=gen_id,
        max_length=22,
        verbose_name='Callback ID',
        help_text='ID колбека',
        editable=False,
    )

    class Meta:
        abstract = True


class CallbackMakeBet(Callback):
    session = models.ForeignKey(
        to=Sessions,
        on_delete=models.CASCADE,
        related_name='callbacks_makebet',
        related_query_name='callback_makebet',
        verbose_name='Session',
        help_text='Сессия, к которой относится колбек',
    )

    def __str__(self):
        return f'Session: {self.session} Callback: {self.id}'

    class Meta:
        verbose_name = 'Callback Make Bet'
        verbose_name_plural = 'Callbacks Make Bet'


class CallbackChooseAmount(Callback):
    session = models.ForeignKey(
        to=Sessions,
        on_delete=models.CASCADE,
        related_name='callbacks_chooseamount',
        related_query_name='callback_chooseamount',
        verbose_name='Session',
        help_text='Сессия, к которой относится колбек',
    )
    amount = models.IntegerField(
        default=0,
        verbose_name='Amount',
        help_text='Сумма ставки',
    )

    def __str__(self):
        return f'Session: {self.session} Callback: {self.id}'

    class Meta:
        verbose_name = 'Callback Choose Amount'
        verbose_name_plural = 'Callbacks Choose Amount'


class CallbackCancelBet(Callback):
    session = models.ForeignKey(
        to=Sessions,
        on_delete=models.CASCADE,
        related_name='callbacks_cancelbet',
        related_query_name='callback_cancelbet',
        verbose_name='Session',
        help_text='Сессия, к которой относится колбек',
    )

    def __str__(self):
        return f'Session: {self.session} Callback: {self.id}'

    class Meta:
        verbose_name = 'Callback Cancel Bet'
        verbose_name_plural = 'Callbacks Cancel Bet'


class CallbackMakeSpin(Callback):
    session = models.ForeignKey(
        to=Sessions,
        on_delete=models.CASCADE,
        related_name='callbacks_makespin',
        related_query_name='callback_makespin',
        verbose_name='Session',
        help_text='Сессия, к которой относится колбек',
    )

    def __str__(self):
        return f'Session: {self.session} Callback: {self.id}'

    class Meta:
        verbose_name = 'Callback Make Spin'
        verbose_name_plural = 'Callbacks Make Spin'


class CallbackCloseSession(Callback):
    session = models.ForeignKey(
        to=Sessions,
        on_delete=models.CASCADE,
        related_name='callbacks_closesession',
        related_query_name='callback_closesession',
        verbose_name='Session',
        help_text='Сессия, к которой относится колбек',
    )

    def __str__(self):
        return f'Session: {self.session} Callback: {self.id}'

    class Meta:
        verbose_name = 'Callback Close Session'
        verbose_name_plural = 'Callbacks Close Session'
