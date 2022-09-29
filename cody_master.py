import datetime
import os
import pickle
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from pyxlsb import open_workbook as open_xlsb
import shutil
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import pandas as pd


def download_data(request, file, suffix):
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    # The file has been downloaded into RAM, now save it in a file
    fh.seek(0)
    with open('data/' + file["files"][0]["name"].replace("/","-") + suffix , 'wb') as f:
        shutil.copyfileobj(fh, f, length=131072)
    print("Downloaded: ", file["files"][0]["name"])     

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data



def login():
    creds = None
    # The file token.pickle stores the
    # user's access and refresh tokens. It is
    # created automatically when the authorization
    # flow completes for the first time.

    # Check if file token.pickle exists
    if os.path.exists('token.pickle'):
        # Read the token from the file and
        # store it in the variable self.creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials are available,
    # request the user to log in.
    if not creds or not creds.valid:

        # If token is expired, it will be refreshed,
        # else, we will request a new one.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # Save the access token in token.pickle
        # file for future usage
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# # Connect to the API service
service = build('drive', 'v3', credentials=login())

# # request a list of first N files or
# # folders with name and id from the API.


form = st.form(key="annotation")    
with form:
    uploaded_file = st.file_uploader("Please upload the Info File")
    cols = st.columns((1, 1))
    
    starting_date = cols[0].date_input(
         "Initial Date",
#          datetime.date(2022, 7, 6))
        datetime.datetime.today()) 
    ending_date = cols[1].date_input(
         "End Date",
         datetime.date(2019, 7, 9))

    bug_type = cols[0].selectbox(
        "Add All Sheets:", ["True", "False"], index=1
    )
    
    submitted = st.form_submit_button(label="Submit")  

    
if submitted:
    if uploaded_file is not None:
#         try:
        info_master = pd.read_excel(uploaded_file)
        st.table(info_master.head(3))

        for col in info_master.columns.to_list():
          if "Unnamed" in col:
            del info_master[col]

        sheet_names = info_master["Sheet Name"].unique()
        sheet_names_short = [x.lstrip().rstrip() for x in sheet_names if str(x)!="nan"]
        
        for file_name in sheet_names:
            file = service.files().list( q =  "name = '" + file_name + "'", includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
            if len(file) != 0:
                try:
                    request = service.files().export_media(fileId=file["files"][0]['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    download_data(request, file, ".xlsx")
                except:  
                    request = service.files().get_media(fileId=file["files"][0]['id'])
                    download_data(request, file, "")
            else:
                print("File " + file_name + " not found!")


#         df_xlsx = to_excel(dataframe)
#         st.download_button("📥 Download Master File", df_xlsx, file_name = 'master_file.xlsx')
#         except:
#             st.write("Excel file not valid, please upload another one")
