from config import GOOGLE_ACCESS_TOKEN_JSON_PATH, GOOGLE_DOC_WRITER_EMAIL
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def upload_to_google(db_conn, episode_id, title, overwrite):
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT transcript, doc_link FROM transcripts WHERE id = ?", (episode_id,))
        transcript_data = cursor.fetchone()
        if not transcript_data:
            print("Transcript not found in database.")
            return None
        transcript, existing_doc_link = transcript_data

        creds = service_account.Credentials.from_service_account_file(GOOGLE_ACCESS_TOKEN_JSON_PATH)
        scoped_creds = creds.with_scopes(['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])

        docs_service = build('docs', 'v1', credentials=scoped_creds)

        if existing_doc_link and overwrite:
            document_id = existing_doc_link.split('/')[-1]
        else:
            body = {
                'title': title
            }
            doc = docs_service.documents().create(body=body).execute()
            document_id = doc['documentId']

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': transcript
                }
            }
        ]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        drive_service = build('drive', 'v3', credentials=scoped_creds)

        # Grant writer access to your email address
        writer_permissions = {
            'role': 'writer',
            'type': 'user',
            'emailAddress': GOOGLE_DOC_WRITER_EMAIL
        }
        drive_service.permissions().create(fileId=document_id, body=writer_permissions).execute()

        # Grant reader access to anyone with the link
        reader_permissions = {
            'role': 'reader',
            'type': 'anyone'
        }
        drive_service.permissions().create(fileId=document_id, body=reader_permissions).execute()

        doc_link = f"https://docs.google.com/document/d/{document_id}"
        print(f"Transcript uploaded to Google Docs: {doc_link}")

        cursor.execute("UPDATE transcripts SET doc_link = ? WHERE id = ?", (doc_link, episode_id))
        db_conn.commit()

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
