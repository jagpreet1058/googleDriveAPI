from google_api import GoogleAPI
import os

g = GoogleAPI()

sourceMasterFolderID = '1ztlL4Cq0hUf8eEtIubk5BRIkZXgV1ZbD'
destinationMasterFolderID = '1kKHAC2HmlcgNdh2P94JQClhdCZ3spMsM' #Change this to your new destination folder ID

source_folders = g.listFilesInFolder(sourceMasterFolderID)['files']
print('There are {} folders at the source end'.format(len(source_folders)))

dest_folders = g.listFilesInFolder(destinationMasterFolderID, trashed=False)['files']
print('There are {} folders at the destination end'.format(len(dest_folders)))
dest_foldernames = [f['name'] for f in dest_folders]

for folder in source_folders:
    if folder['name'] not in dest_foldernames:
        print('Processing Folder - {}'.format(folder['name']))
        destSubFolderID = g.createFolder(folderName=folder['name'], parentFolderId=destinationMasterFolderID)
        mp3files = g.listFilesInFolder(folder['id'])['files']
        for mp3file in mp3files:
            g.downloadFile(fileId=mp3file['id'], name=mp3file['name'])
            g.uploadFileToFolder(folderID=destSubFolderID, fileName=mp3file['name'], filePath=mp3file['name'])
            os.remove(mp3file['name'])
        break  # Remove this break statement when test run with 1 file went fine.
