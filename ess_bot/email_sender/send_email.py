import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from email_config import *

def send_email_with_screenshot(duty=None, sender_email=EMAIL_SENDER_LOGIN, sender_password=EMAIL_SENDER_PASS):
    message = EmailMessage()
    message['Subject'] = f"Работы на мою РГ."
    message['From'] = sender
    message['To'] = "support@infinnity.ru"
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
    mail_lib.login(sender, sender_password)
    mail_lib.send_message(message)
