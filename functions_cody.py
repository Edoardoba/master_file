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



def get_sheet_name(info_master, element):
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
