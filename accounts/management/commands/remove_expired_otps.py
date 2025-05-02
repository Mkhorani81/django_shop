from django.core.management.base import BaseCommand
from accounts.models import OtpCode
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    help = 'remove all expired OTP codes'

    def handle(self, *args, **options):
        expire_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
        OtpCode.objects.filter(created__lt=expire_time).delete()
        self.stdout.write('all expired OTP codes removed')