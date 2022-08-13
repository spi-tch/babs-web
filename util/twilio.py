import os

from twilio.rest import Client

client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))


def send_verification_code(phone_number, channel, code):
  try:
    message = client.messages.create(
      from_=f'{channel}:{os.getenv("TWILIO_WA_PHONE_NUMBER")}',
      body=f"""
      Hello there. My name is Babs, you requested my assistance.
      I'm glad nice to be chatting with you, I'm here to help.
      *Kindly enter the code: ```{code}``` on the web app.*
      
      If you did not request this message, kindly ignore and I won't bother you.""",
      to=f'{channel}:{phone_number}'
    )
    return message.sid
  except Exception as e:
    print(e)
