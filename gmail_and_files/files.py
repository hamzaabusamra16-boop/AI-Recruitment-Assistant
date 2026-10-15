import os
import io
import base64
import email
import mimetypes
import extract_msg
import docx
import re
from pypdf import PdfReader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import random
from googleapiclient.errors import HttpError

def create_message(sender ,to,subject,messge_text ):
    message= MIMEText(messge_text)
    message["from"]= sender
    message["to"]=to
    message["subject"]=subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {
        "raw": raw_message.decode('utf-8')
    }
def create_drafts(service, user_id, message_body):
    try:
        message = {"message" :message_body}
        drafts=service.users().derfts().create(userId=user_id,body=message).execute()
        print("Draft id: %s\nDraft message: %s" % (drafts['id'], drafts['message']))
        return drafts
    except Exception as ex:
        print('An error occurred: %s' % ex)
        return None
def sender_message(service, user_id, message ):
    try:
        sent_message=service.users().derfts().create(userId=user_id,body=message).execute()
        print('Message Id: %s' % message['id'])
        return sent_message
    except Exception as ex:
        print('An error occurred: %s' % ex)
        return None
def create_message_with_attachment(sender, to, subject, message_text, file):
        ALLOWED_TYPES = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        msg = MIMEText(message_text)
        message.attach(msg)
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        if content_type not in ALLOWED_TYPES:
            print("لا يمكنك تحميل هدا الملف الا بصيغة bdf او word")
            return None
        main_type, sub_type = content_type.split('/', 1)
        with open (file,"rb") as fp:
            attachment_data = fp.read()
        attachment = MIMEBase(main_type, sub_type )
        attachment.set_payload(attachment_data)
        encoders.encode_base64(attachment)   
        filename = os.path.basename(file)
        attachment.add_header(
             "Content-Disposition",
            "attachment",
            filename = filename
        )
        message.attach(attachment)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {'raw': raw_message}
def get_messages(service, user_id):
    try:
       return service.users().messages().list(userId=user_id).execute()
    except Exception as error:
      print('An error occurred: %s' % error)
      return None

def get_message(service, user_id, msg_id):
    try:
        return service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
    except Exception as error:
      print('An error occurred: %s' % error)
      return None
def get_mime_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                format='raw').execute()
        print('Message snippet: %s' % message['snippet'])
        msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
        mime_msg = email.message_from_string(msg_str)
        return mime_msg
    except Exception as error:
        print('An error occurred: %s' % error)
        return None

def get_attachments(service, user_id, msg_id, store_dir):
    os.makedirs(store_dir, exist_ok=True)

    def execute_with_retry(request, retries=4):
        for attempt in range(retries):
            try:
                return request.execute()
            except HttpError as error:
                if error.resp.status not in (403, 429, 500, 503):
                    raise

                if attempt == retries - 1:
                    raise

                delay = (2 ** attempt) + random.random()
                print(f"Gmail API limit/server error. Retrying in {delay:.1f}s...")
                time.sleep(delay)

    try:
        message = execute_with_retry(
            service.users().messages().get(
                userId=user_id,
                id=msg_id,
                format="full",
            )
        )

        def save_parts(parts):
            for part in parts:
                filename = part.get("filename")
                body = part.get("body", {})
                attachment_id = body.get("attachmentId")

                if filename and attachment_id:
                    attachment = execute_with_retry(
                        service.users().messages().attachments().get(
                            userId=user_id,
                            messageId=msg_id,
                            id=attachment_id,
                        )
                    )

                    file_data = base64.urlsafe_b64decode(
                        attachment["data"]
                    )

                    safe_filename = os.path.basename(filename)
                    path = os.path.join(store_dir, safe_filename)

                    with open(path, "wb") as file:
                        file.write(file_data)

                    print(f"Saved attachment: {safe_filename}")
                    time.sleep(0.2)

                save_parts(part.get("parts", []))

        payload = message.get("payload", {})
        save_parts(payload.get("parts", []))

    except Exception as error:
        print(f"Failed to download attachments for {msg_id}: {error}")
        return None


def process_student_emails(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        text = ""

        if filename.lower().endswith(".msg"):
            with extract_msg.Message(file_path) as read_files:
                print(f"فحص إيميل الطالب: {read_files.sender}")

                for attachment in read_files.attachments:
                    attachment_name = (
                        attachment.longFilename
                        or attachment.shortFilename
                        or ""
                    )

                    if attachment_name.lower().endswith(".pdf"):
                        file = io.BytesIO(attachment.data)
                        reader = PdfReader(file)
                        text = ""

                        for page in reader.pages:
                            text += (page.extract_text() or "") + "\n"

                    elif attachment_name.lower().endswith(".docx"):
                        file = io.BytesIO(attachment.data)
                        document = docx.Document(file)
                        text = ""

                        for paragraph in document.paragraphs:
                            text += paragraph.text + "\n"

                    else:
                        continue

                    print(f"معالجة السيرة الذاتية: {attachment_name}")
                    extract_info(text)

        elif filename.lower().endswith(".pdf"):
            reader = PdfReader(file_path)

            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"

            print(f"معالجة السيرة الذاتية: {filename}")
            extract_info(text)

        elif filename.lower().endswith(".docx"):
            document = docx.Document(file_path)

            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"

            print(f"معالجة السيرة الذاتية: {filename}")
            extract_info(text)


def extract_info(text):
    patterns = {
        "Name": r"Name:\s*(.+)",
        "Email": r"Email:\s*([\w.-]+@[\w.-]+\.\w+)",
        "Phone": r"Phone:\s*([+()\d\s-]+)",
        "Skills": r"Skills:\s*(.+)",
        "Certificates": r"Certificates:\s*(.+)",
        "Experience": r"Experience:\s*(.+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        value = match.group(1).strip() if match else None
        print(f"{field}: {value}")
