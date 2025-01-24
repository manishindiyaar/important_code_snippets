# Making API call for sending Test mail
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

message = Mail(
    from_email='info@bladexlab.com',
    to_emails='manishindiyaar@gmail.com',
    subject='Test Email',
    plain_text_content='This is a test email'
)

try:
    sg = SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(str(e))

    