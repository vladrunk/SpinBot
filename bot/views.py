from django.http import JsonResponse

from .bot import bot


def start_bot_view(request):
    if not bot.running:
        bot.start()

    return JsonResponse({'message': 'Bot started'})


def stop_bot_view(request):
    if bot.running:
        bot.stop()

    return JsonResponse({'message': 'Bot stopped'})


