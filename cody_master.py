import datetime
import os
import pickle
import streamlit as st
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from pyxlsb import open_workbook as open_xlsb
import shutil
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import pandas as pd
import numpy as np
from io import BytesIO

path = "data/"
# Initialize Master File
col_names =  ["Sheet Name", "Date", "ASIN", "ASIN URL", "Product Title", "Source", "Source URL", "Source Title", "Product Category","Buy Cost", "Sell Price", "Projected Net Profit", "ROI", "Promo Codes", "Cashback","Notes"]
master_file  = pd.DataFrame(columns = col_names)

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


def build_master_file(master_file, data, filename, sheetname, timestampp):
  col_names =  ["Sheet Name", "Date"]
  temp_data  =  pd.DataFrame(np.nan, index = np.arange(len(data)), columns = col_names)
  temp_data["Sheet Name"], temp_data["Date"] = filename, timestampp
  columns_list = info_master[info_master["Sheet Name"]==filename].reset_index(drop=True).loc[0].to_list()
  for column in range(3, len(columns_list)):
    if columns_list[column] != "-":
      temp_data[info_master.columns.to_list()[column]] = data[[columns_list[column]]]
    else:
      temp_data[info_master.columns.to_list()[column]] = "Not Defined"

  master_file = master_file.append(temp_data)
  master_file = master_file[master_file.isnull().sum(axis=1) < 7]
  return master_file


def read_data(file, sheet):
  if sheet[0]!= "None":
    for format in sheet:
      try:
        data = pd.read_excel(str(file), format)
      except:
        data = pd.read_excel(str(file))
  else:
    data = pd.read_excel(str(file))

  if 'Unnamed: 1' in data.columns.to_list():
    data = data[data.isnull().sum(axis=1) < 7]
    new_header = data.iloc[0]
    data = data[1:]
    data.columns = new_header 
    data.columns = data.columns.str.rstrip().str.lstrip()
    return data.reset_index(drop=True), sheet
  else:
    data.columns = data.columns.str.rstrip().str.lstrip()
    return data.reset_index(drop=True), sheet



def post_processing(master_file):
  master_file["Product Category"] = master_file["Product Category"].str.replace("\r","")
  master_file = master_file[master_file["ASIN"]!="ASIN"].reset_index(drop=True)
  master_file = master_file.drop_duplicates().reset_index(drop=True)
  return master_file



def get_sheet_name(element):
  format = info_master[info_master["Sheet Name"]==element].reset_index(drop=True)["Sheet Format"].item()
  if format == "-": return ["None"]
  elif format == "MM.DD": return ([day.strftime('%-m.%d'), day.strftime('%m.%d'), day.strftime('%-m.%-d'), day.strftime('%m.%-d')])
  elif format == "MONTH DD, YYYY": return [day.strftime('%B %d, %Y'), day.strftime('%B %-d, %Y')]
  elif format == "DDMMYYYY": return [day.strftime('%d%m%Y'), day.strftime('%-d%m%Y'), day.strftime('%d%-m%Y'), day.strftime('%-d%-m%Y')]


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
        datetime.datetime.today()) 
    ending_date = cols[1].date_input(
         "End Date",
         datetime.datetime.today())

    bug_type = cols[0].selectbox(
        "Add All Sheets:", ["True", "False"], index=1
    )
    
    submitted = st.form_submit_button(label="Submit")  

if submitted:
    if uploaded_file is not None:
        info_master = pd.read_excel(uploaded_file)
        st.table(info_master.head(3))

        for col in info_master.columns.to_list():
          if "Unnamed" in col:
            del info_master[col]

        sheet_names = info_master["Sheet Name"].unique()
        sheet_names_short = [x.lstrip().rstrip() for x in sheet_names if str(x)!="nan"]
        
        
        for file_name in sheet_names:
            file = service.files().list( q =  "name = '" + file_name.replace("'","\\'").replace("\"","\\'") + "'", includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
            if len(file["files"]) != 0:
                try:
                    request = service.files().export_media(fileId=file["files"][0]['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    download_data(request, file, ".xlsx")
                except:  
                    request = service.files().get_media(fileId=file["files"][0]['id'])
                    download_data(request, file, "")
            else:
                print("File " + file_name + " not found!")

                
                
        info_master["Sheet Name"] = [str(x).replace("/","-").lstrip().rstrip() for x in info_master["Sheet Name"]]

        add_all_sheets = bug_type
        days_to_be_considered = ""
        
        starting_date = starting_date.strftime('%Y/%m/%d')
        ending_date = ending_date.strftime('%Y/%m/%d')
        
        if starting_date == datetime.datetime.today().strftime('%Y/%m/%d'):
            days_to_be_considered = ""
        else:
            days_to_be_considered = str(starting_date) + "-" + str(ending_date) 
            
        if days_to_be_considered != "" and add_all_sheets == str(False):
          initial_date = datetime.datetime.strptime(days_to_be_considered.split("-")[0], '%Y/%m/%d')
          final_date = datetime.datetime.strptime(days_to_be_considered.split("-")[1], '%Y/%m/%d')
          dates_list = []
          diff = final_date - initial_date
          for date in range(diff.days + 1):
              dates_list.append((initial_date + timedelta(date)).strftime('%Y/%m/%d'))
        else:
          day = datetime.datetime.today()



        for element in os.listdir("data/"):
          if element.endswith('.xlsx'):
                 
            if add_all_sheets == str(False):
        # Normal scenario, only daily leads
              if days_to_be_considered == "":
                try:
                  sheet = get_sheet_name(element.replace(".xlsx", ""))
                  data, sheetname = read_data(path + element, sheet)
                  master_file = build_master_file(master_file, data, element.replace(".xlsx", ""), sheetname, day.strftime('%d/%m/%Y')).reset_index(drop = True)
                  print("Done " + element)
                except Exception as e:
                  print("File " + element + " not processed")
              else:
        # Retrieve all leads from a Date Range
                docs_to_ignore = []
                for selected_date in dates_list:
                  try:
                      if element not in docs_to_ignore:
                        day = datetime.datetime.strptime(selected_date, '%Y/%m/%d')
                        sheet = get_sheet_name(element.replace(".xlsx", ""))
                        if sheet == ["None"]: docs_to_ignore.append(element)             
                        data, sheetname = read_data(path + element, sheet)
                        master_file = build_master_file(master_file, data, element.replace(".xlsx", ""), sheetname, day.strftime('%d/%m/%Y')).reset_index(drop = True)           
                  except:
                    pass
                  print("Done " + element + " " + selected_date)
        # Scan all sheets in the Excel Files
            else:
              try:
                for sheet in pd.ExcelFile("data/" + element).sheet_names:
                  data, sheetname = read_data(path + element, [sheet])
                  if len(pd.ExcelFile("data/" + element).sheet_names) > 1:
                    master_file = build_master_file(master_file, data, element.replace(".xlsx", ""), sheetname, sheet).reset_index(drop = True)
                  else:
                    master_file = build_master_file(master_file, data, element.replace(".xlsx", ""), sheetname, day).reset_index(drop = True)

                  print("Done " + element + " " + sheet)
              except:
                pass

        master_file = post_processing(master_file)          
        master_file = to_excel(master_file)        
        st.download_button("📥 Download Master File", master_file, file_name = 'master_file.xlsx')    

#         df_xlsx = to_excel(dataframe)
#         st.download_button("📥 Download Master File", df_xlsx, file_name = 'master_file.xlsx')
#         except:
#             st.write("Excel file not valid, please upload another one")
