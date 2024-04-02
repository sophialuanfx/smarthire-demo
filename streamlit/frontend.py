# frontend.py

import streamlit as st
import requests
import pandas as pd
import altair as alt
import base64
import os

import sys
sys.path.insert(0,'C:/Users/sophi/ChaliceProject/smarthire-demo/app/chalicelib')
from model import resumeSum, resuemJobMatch

def main():
    st.title('Smart Hire')

    # Load data 
    df = pd.read_csv("../app/raw_google_1129.csv", usecols=['title'])

    # Count the occurrences of each title
    title_counts = df['title'].value_counts().reset_index()
    title_counts.columns = ['title', 'count']

    # Create Altair chart
    chart = alt.Chart(title_counts).mark_bar().encode(
        x='title',
        y='count'
    ).properties(
        title='Title Counts'
    )

    # Display chart in Streamlit
    st.write("Number of Data Job")
    st.altair_chart(chart, use_container_width=True)

    selected_option = st.multiselect(
    'Select Job Location',
        ['Toronto', 'Montreal', 'Vancourver','Calgary','Edmonton']
    )
    if st.button('select'):
        st.experimental_rerun() 
        st.experimental_set_query_params(selected_options=selected_option)

    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("Upload"):
            try:
                # Read file content
                file_content = uploaded_file.read()
                filename = uploaded_file.name



                encoded_content = base64.b64encode(file_content).decode('utf-8')

                # Send filename and encoded content as JSON payload
                data = {'filename': filename, 'content': encoded_content}
                
                # Send the POST request
                response = requests.post('https://3qdperjzt2.execute-api.us-west-2.amazonaws.com/api/upload', json=data)

                # Handle response
                if response.status_code == 200:
                    st.success("File uploaded and processed successfully!")
                    result = resumeSum(filename, file_content)  # Pass file content as bytes
                    st.write("Resume Processing Result: ", result)

                else:
                    st.error("Error uploading file. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


