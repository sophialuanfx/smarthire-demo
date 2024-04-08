# frontend.py

import streamlit as st
import requests
import pandas as pd
import altair as alt
import base64
import os
import tempfile
import re

import sys
sys.path.insert(0,'C:/Users/sophi/ChaliceProject/smarthire-demo/app/chalicelib')
from model import resumeSum, resuemJobMatch

if 'rematch_button_click_count' not in st.session_state:
    st.session_state.rematch_button_click_count = 0

def main():
    st.title('Smart Hire')
    st.markdown("<br>", unsafe_allow_html=True)
    # Load data 
    df = pd.read_csv("../app/raw_google_final.csv", usecols=['title'])
    substrings_to_match = ["Data Analyst", "Data Engineer", "Data Scientist", "Software Developer", "Product Manager", "Digital Marketer"]

    def extract_main_title(title):
        for substring in substrings_to_match:
            if substring.lower() in title.lower():
                return substring
        return "Other"
    
    df['Job Title'] = df['title'].apply(extract_main_title)
    title_counts = df['Job Title'].value_counts().reset_index()
    title_counts.columns = ['Job Title', 'count']

    # Create Altair chart
    chart = alt.Chart(title_counts).mark_bar().encode(
        x='Job Title',
        y='count'
    ).properties(
        title='Data and Software Job Positions in Last 7 Days'
    )
    st.altair_chart(chart, use_container_width=True)

    #select job tag
    default_location=['Toronto', 'Montreal', 'Vancourver','Calgary','Edmonton']
    selected_options = st.multiselect(
    'Optional: Select Job Location',
        ['Toronto', 'Montreal', 'Vancourver','Calgary','Edmonton'],
        default=default_location
    )
    #st.write(selected_options)
    
    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked =False
    
    if uploaded_file is not None:
        if (st.button("Upload", on_click=callback) or st.session_state.button_clicked):

            # Read pdf file content
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            encoded_content = base64.b64encode(file_content).decode('utf-8')


            # Send filename and encoded content as JSON payload
            data = {'filename': filename, 'content': encoded_content}
            
            # Send the POST request to backend
            response = requests.post('https://3qdperjzt2.execute-api.us-west-2.amazonaws.com/api/upload', json=data)

            # Handle response
            if response.status_code == 200:
                st.success("File uploaded and processed successfully!")
            else:
                st.error("Error uploading file. Please try again.")
            
            #handle reusme summary
            st.markdown("<hr>", unsafe_allow_html=True)
            
            with st.spinner("Running Resume Summary..."):
                file_path = save_uploaded_file(uploaded_file)
                result=resumeSum(filename, file_path)
                st.text(result)
            st.success("Resume summary completed.")

            st.markdown("<hr>", unsafe_allow_html=True)
            

            with st.spinner("Finding positions based on resume summary..."):
                rematch(default_location, selected_options, result)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.write("Not satisfied with the matched job? ")
            if st.button("Rematch"):
                st.session_state.rematch_button_click_count += 1
            #st.write(f"Rematch button clicked {st.session_state.rematch_button_click_count} times")

def callback():
    st.session_state.button_clicked =True

# Create a temporary directory to store the uploaded file
def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    # Save the file to the temporary location
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    return file_path

def rematch(default_location, selected_options, result):
    # Call resuemJobMatch function with appropriate parameters
    if not selected_options or selected_options == default_location:
        second_result = resuemJobMatch(result, 'C:/Users/sophi/ChaliceProject/smarthire-demo/app/raw_google_final.csv', default_location)
    else:
        second_result = resuemJobMatch(result, 'C:/Users/sophi/ChaliceProject/smarthire-demo/app/raw_google_final.csv', selected_options)
    
    st.markdown(second_result, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


