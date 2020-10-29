import pickle
import io
import os
import json
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging as logger

logger.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.appdata']

class GoogleAPI(object):
    def __init__(self):
        self.googleDrive = self.setCredsUsingUI()

    def setCredsUsingUI(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.info('Token does not exist or expired, user need to use Google Chrome UI to authenticate.')
                flow = InstalledAppFlow.from_client_secrets_file('client_id.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds)
        return service

    def setCredsUsingServiceAccount(self):
        cred_file = open('credentials/seeburg-5aa23a25f67c.json').read()
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(cred_file), SCOPES)
        http = creds.authorize(httplib2.Http())
        service = build('drive', 'v3', http=http, cache_discovery=False)
        return service

    def getDetails(self, ID):
        results = self.googleDrive.files().get(fileId=ID).execute()
        return results

    def listFilesInFolder(self, folderID):
        q = "'{}' in parents".format(folderID)
        fields = "files(id, name)"
        results = self.googleDrive.files().list(pageSize=1000, q=q, fields=fields).execute()
        return results

    def downloadFile(self, fileId, name):
        request = self.googleDrive.files().get_media(fileId=fileId)
        fh = io.FileIO(name,mode = 'w')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        if done:
            return True
        else:
            return False

    def createFolder(self, folderName, parentFolderId):
        file_metadata = {
            'name': folderName,
            'parents': [parentFolderId],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        response = self.googleDrive.files().create(body=file_metadata,
                                            fields='id').execute()
        folderId = response.get('id')
        logger.info('Created Folder {} with ID: {}'.format(folderName, folderId))
        if folderId:
            return folderId
        else:
            return False

    def deleteFolder(self, id):
        try:
            self.googleDrive.files().delete(fileId=id).execute()
        except Exception as error:
            print('An error occurred: {}'.format(error))

    def uploadFileToFolder(self, folderID, fileName, filePath):
        file_metadata = {
            'name': fileName,
            'parents': [folderID]
        }
        media = MediaFileUpload(filePath,
                                mimetype='audio/mpeg',
                                resumable=True)
        response = self.googleDrive.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        fileId = response.get('id')
        logger.info('Uploaded File {} with ID: {}'.format(fileName, fileId))
        if fileId:
            return fileId
        else:
            return False