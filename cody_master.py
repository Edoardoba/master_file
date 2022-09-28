
from __future__ import print_function
import streamlit as st
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

class DriveAPI:
    global SCOPES

    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self):

        # Variable self.creds will
        # store the user access token.
        # If no valid token found
        # we will create one.
        self.creds = None
        self.lists={}

        # The file token.pickle stores the
        # user's access and refresh tokens. It is
        # created automatically when the authorization
        # flow completes for the first time.

        # Check if file token.pickle exists
        if os.path.exists('token.pickle'):
            # Read the token from the file and
            # store it in the variable self.creds
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials are available,
        # request the user to log in.
        if not self.creds or not self.creds.valid:

            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle
            # file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)

        # request a list of first N files or
        # folders with name and id from the API.
        results = self.service.files().list(
            pageSize=100).execute()
        items = results.get('files', [])
        self.lists=items
        # print a list of files

        print("Here's a list of files: \n")
        print(*items, sep="\n", end="\n\n")

# def to_excel(df):
#     output = BytesIO()
#     writer = pd.ExcelWriter(output, engine='xlsxwriter')
#     df.to_excel(writer, index=False, sheet_name='Sheet1')
#     workbook = writer.book
#     worksheet = writer.sheets['Sheet1']
#     format1 = workbook.add_format({'num_format': '0.00'}) 
#     worksheet.set_column('A:A', None, format1)  
#     writer.save()
#     processed_data = output.getvalue()
#     return processed_data



st.title('Master File Tool')

obj = DriveAPI()
# required_lists_of_files_with_id=obj.lists
# st.write(required_lists_of_files_with_id)


st.write('OKKK')


# import streamlit as st
# from google.oauth2 import service_account
# from google.cloud import storage

# # Create API client.
# credentials = service_account.Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"]
# )
# # client = storage.Client(credentials=credentials)

# drive = GoogleDrive()
# drive_service = build('drive', 'v3', credentials=credentials)

# drive.ListFile({ "q":"title='" + "OA Hunt Gold".replace("'","\\'").replace("\"","\\'") + "'", "includeItemsFromAllDrives":"True", "supportsAllDrives":"True", "corpora":"allDrives"}).GetList()


# for file_name in "OA Hunt Gold":
#     file = drive.ListFile({ "q":"title='" + file_name.replace("'","\\'").replace("\"","\\'") + "'", "includeItemsFromAllDrives":"True", "supportsAllDrives":"True", "corpora":"allDrives"}).GetList()
#     if len(file) != 0:
#       try:
#         request = drive_service.files().export_media(fileId=file[0]['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         download_data(request, file[0], ".xlsx")
#         print("File " + file_name + " downloaded!")
#       except:  
#         request = drive_service.files().get_media(fileId=file['id'])
#         download_data(request, file[0], "")
#         print("File " + file_name + " downloaded!")
#     else:
#       print("File " + file_name + " not found!")


st.write("AA")

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth() # client_secrets.json need to be in the same directory as the script
# drive = GoogleDrive(gauth)    

# form = st.form(key="annotation")    
# with form:
#     uploaded_file = st.file_uploader("Please upload the Info File")
#     cols = st.columns((1, 1))
    
#     starting_date = cols[0].date_input(
#          "Initial Date",
#          datetime.date(2019, 7, 6))
#     ending_date = cols[1].date_input(
#          "End Date",
#          datetime.date(2019, 7, 9))

#     bug_type = cols[0].selectbox(
#         "Add All Sheets:", ["True", "False"], index=1
#     )
    
#     submitted = st.form_submit_button(label="Submit")  

    
# if submitted:
#     if uploaded_file is not None:
# #         try:
#         dataframe = pd.read_excel(uploaded_file)
#         st.table(dataframe)


#         df_xlsx = to_excel(dataframe)
#         st.download_button("📥 Download Master File", df_xlsx, file_name = 'master_file.xlsx')
#         except:
#             st.write("Excel file not valid, please upload another one")
