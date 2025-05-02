from datetime import timedelta, datetime
import pytz
from celery import shared_task
from .models import OtpCode

@shared_task
def remove_expired_otp_codes():
    expire_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
    OtpCode.objects.filter(created__lt=expire_time).delete()