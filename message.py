from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

from service import get_service

service = get_service()


class Message:
	"""Create a message for an email.

	Attributes:
		sender: Email address of the sender.
		recipient: Email address of the receiver.
		subject: The subject of the email message.
		message_text: The text of the email message.
	"""
	def __init__(self, sender, recipient, subject, message_text):
		self.sender = sender
		self.recipient = recipient
		self.subject = subject
		self.message_text = message_text

		mime_message = MIMEMultipart()
		mime_message['from'] = sender
		mime_message['to'] = recipient
		mime_message['subject'] = subject
		mime_message.attach(MIMEText(message_text, 'plain'))
		raw_string = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

		self.message = {'raw': raw_string}

	def send_message(self):
		sent_message = service.users().messages().send(
			userId=self.sender,
			body=self.message).execute()
		return sent_message

if __name__ == '__main__':
	msg = Message('me', 'patrickoeijan21@gmail.com', 'Automatic Message','test')
	print(msg.send_message())