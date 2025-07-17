import pdb
import time
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def download_attachment(service, msg_id, attachment_id, filename):
	print(msg_id, attachment_id, filename)
	attachment = service.users().messages().attachments().get(
		userId="me", messageId=msg_id, id=attachment_id
	).execute()
	file_data = attachment['data']
	import base64
	file_data = base64.urlsafe_b64decode(file_data.encode('UTF-8'))
	with open(filename, 'wb') as f:
		f.write(file_data)


def main():
	"""Shows basic usage of the Gmail API.
	Lists the user's Gmail labels.
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				"credentials.json", SCOPES
			)
			creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
	with open("token.json", "w") as token:
		token.write(creds.to_json())

	try:
		# Call the Gmail API
		service = build("gmail", "v1", credentials=creds)

		# results = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
		a_month_ago = int(time.time()) - 30 * 24 * 60 * 60
		results = service.users().messages().list(userId='me', q=f'subject:信用卡 subject:帳單 has:attachment after:{a_month_ago}').execute()
		messages = results.get("messages", [])

		for idx, msg in enumerate(messages):
			msg_id = msg['id']
			msg_detail = service.users().messages().get(userId="me", id=msg_id, format="full", metadataHeaders=["Subject"]).execute()
			headers = msg_detail.get("payload", {}).get("headers", [])
			subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
			print(f"Downloading {subject} attachment")

			for p_id, part in enumerate(msg_detail.get('payload', {}).get('parts', [])):
				if part.get('filename'):
					print(part.get('filename'))
					attachment_id = part['body'].get('attachmentId')
					download_attachment(service, msg_id, attachment_id, f"{subject[:2]}_{p_id}_{idx}.pdf")

	except HttpError as error:
		# TODO(developer) - Handle errors from gmail API.
		print(f"An error occurred: {error}")


if __name__ == "__main__":
	main()