import streamlit as st
import pandas as pd
import numpy as np
import datetime


st.title('Master File Tool')

st.write("CIAOOOOOOOO")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_excel(uploaded_file.name)
    st.table(dataframe.head(3))
    

    
    
    
    

starting_date = st.date_input(
     "Initial Data",
     datetime.date(2019, 7, 6))
end_date = st.date_input(
     "End Date",
     datetime.date(2019, 7, 6))
st.write(starting_date, end_date)



# st.download_button("AA", dataframe.to_csv("test.csv"))
