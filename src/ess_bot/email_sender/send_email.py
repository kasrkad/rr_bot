import smtplib
from os import remove
from email.message import EmailMessage
from email.utils import make_msgid
from .email_config import *
from ..logger_config.logger_data import create_logger

sender_logger = create_logger(__name__)


def send_email_with_screenshot(duty=None, sender_email=EMAIL_SENDER_LOGIN, sender_password=EMAIL_SENDER_PASS):
    try:
        sender_logger.info("Создаем письмо")
        message = EmailMessage()
        message['Subject'] = f"Работы на мою РГ."
        message['From'] = sender_email
        message['To'] = TARGET_EMAIL
        message.set_content(f'Дежурный: {duty}')
        image_cid = make_msgid()
        message.add_alternative("""\
<html>
  <head></head>
  <body>
    <p>{content}</p>
    <img src="cid:{image_cid}" />
  </body>
</html>
""".format(image_cid=image_cid[1:-1], content=f'Дежурный: {duty}'), subtype='html')
        with open("screenshot_hpsm.jpg",'rb') as img:
            message.get_payload()[1].add_related(img.read(), 'image', 'jpeg',cid=image_cid)

        mail_lib = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        sender_logger.info('Письмо создано, логинимся в сервис отправки')
        mail_lib.login(sender_email, sender_password)
        sender_logger.info('Логин успешен, отправляем сообщение')
        mail_lib.send_message(message)
        sender_logger.info('Сообщение успешно отправлено, удаляем файл вложение.')
        remove('./screenshot_hpsm.jpg')
    except Exception:
        sender_logger.error('При отправке сообщения произошла ошибка', exc_info=True)
        raise
