# frontend.py

import streamlit as st
import requests
import pandas as pd
import altair as alt
import base64
import os
import re
import tempfile

#replace with your own local path
import sys
sys.path.insert(0,'C:/Users/sophi/ChaliceProject/smarthire-demo/app/chalicelib')
from model import resumeSum, resuemJobMatch
sys.path.insert(7,'C:/Users/sophi/ChaliceProject/smarthire-demo/app')
from app import send_email

def main():
    st.title('Smart Hire')
    st.markdown("<br>", unsafe_allow_html=True)
    # Load data 
    df = pd.read_csv("../app/data/raw_google_1129.csv", usecols=['title'])
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

    #email input
    st.write("Subscribe and new job postings will be sent by email.")
    email = st.text_input("Enter your email address below:")
    if email:
        if re.match(r'^[\w\.-]+@[\w\.-]+(\.[\w]+)+$', email):
            st.success("Subscribe successfully!")
        else:
            st.error("Please enter a valid email address.")
    
    st.markdown("<hr>", unsafe_allow_html=True)

    #select job tag
    default_location=['Toronto', 'Montreal', 'Vancourver','Calgary','Edmonton']
    selected_options = st.multiselect(
    'Optional: Select Job Location',
        ['Toronto', 'Montreal', 'Vancourver','Calgary','Edmonton'],
        default=default_location
    )
    
    #upload file
    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
    if uploaded_file is not None:
        if st.button("Upload"):
            # Read pdf file content
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            encoded_content = base64.b64encode(file_content).decode('utf-8')


            # Send filename and encoded content as JSON payload
            data = {'filename': filename, 'content': encoded_content}
            
            #replace with your own Api url
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
            with st.spinner("Finding jobs..."):
                second_result=rematch(selected_options, result)
            if email:
                send_email(email, second_result)
                st.success("Job info sent to email successfully.")

# Create a temporary directory to store the uploaded file
def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    # Save the file to the temporary location
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def rematch(selected_options, result):
    # Call resuemJobMatch function with appropriate parameters
    second_result = resuemJobMatch(result, '../app/data/raw_google_1129.csv', selected_options)
    st.markdown(second_result, unsafe_allow_html=True)
    return second_result


if __name__ == "__main__":
    main()


