from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import RefrigeratorData, Fridge
from .views import send_telegram_message

# Словарь для хранения времени последнего отправленного сообщения по каждому холодильнику
last_sent_messages = {}

@receiver(post_save, sender=RefrigeratorData)
def check_last_update(sender, instance, **kwargs):
    """
    Проверяем, прошло ли более 5 минут с последнего обновления для каждого холодильника.
    Если данных нет более 5 минут, отправляем тревогу в Telegram,
    но только если сообщение ещё не было отправлено за последние 5 минут.
    """
    time_threshold = timezone.now() - timedelta(minutes=30)  # Время ожидания 5 минут

    fridges = Fridge.objects.all()  # Получаем все устройства

    for fridge in fridges:
        last_record = RefrigeratorData.objects.filter(fridge=fridge).order_by('-event_date').first()

        if not last_record or last_record.event_date < time_threshold:
            # Если сообщение уже было отправлено недавно, пропускаем его
            last_message_time = last_sent_messages.get(fridge.id)
            if not last_message_time or timezone.now() - last_message_time > timedelta(minutes=30):
                message = (
                    f"⚠️ {fridge.name} не отправлял данные более 30 минут!"
                )
                send_telegram_message(message)
                last_sent_messages[fridge.id] = timezone.now()  # Обновляем время последнего сообщения
