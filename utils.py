from django.contrib.auth.mixins import UserPassesTestMixin
from kavenegar import *


def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('476970363456306F4872776A5862763270586D576A4377356A764F724E58717876486D72572F744E5372733D')
        params = {
            'sender': '2000660110',
            'receptor' : phone_number,
            'message' : f'{code} کد تایید شما'
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


class IsAdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin