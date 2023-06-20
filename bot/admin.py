from django.contrib import admin
from .models import Users, Sessions, CallbackMakeBet, CallbackChooseAmount, CallbackCancelBet, CallbackMakeSpin, \
    CallbackCloseSession, Combinations


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance')
    search_fields = ('id',)
    ordering = ('id',)  # Сортировка по полю 'id'


@admin.register(Sessions)
class SessionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'user', 'msg_id', 'amount', 'result', 'win', 'close')
    list_filter = ('chat_id', 'user', 'close')  # Фильтры по полям 'chat_id', 'user' и 'close'
    search_fields = ('id', 'chat_id',)
    ordering = ('id',)  # Сортировка по полю 'id'


@admin.register(CallbackChooseAmount)
class CallbackChooseAmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'amount')
    ordering = ('session', 'amount', )  # Сортировка по полю 'session'


@admin.register(CallbackMakeBet, CallbackCancelBet, CallbackMakeSpin, CallbackCloseSession)
class CallbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'session')
    ordering = ('session',)  # Сортировка по полю 'session'


@admin.register(Combinations)
class CombinationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'comb', 'mult')
    list_filter = ('mult',)  # Фильтр по полю 'mult'
    ordering = ('id',)  # Сортировка по полю 'id'
