# Smart Job Info Generator


Generate smart job information from resumes to simplify the job application process. 
Demo Video:(https://drive.google.com/file/d/1mnn3Bqr74i82PNg0mrxYXKPHQp12QqZh/view?usp=sharing)


## Features

- **Altair Chart:** Visualize job data from the last 7 days using Altair charts.
- **Location Filtering:** Filter job postings based on location.
- **Resume Parsing:** Extract relevant information from resumes.
- **Smart Job Suggestions:** Generate tailored job suggestions based on resume content. Allow users to apply directly to suggested jobs from within the application.
- **Job Subscription:** Subscribe to receive job postings directly to your email.


## Installation

```bash
pip install chalice
pip install pandas
pip install apify-client
pip install opensearch-py
pip install langchain
pip install openai
pip install langchainhub
pip install tiktoken
pip install PyPDF2
pip install faiss-cpu
```

## Create a Chalice App
Create a new Chalice project:

```
chalice new-project smarthire
cd smarthire
chalice deploy
```

## Deploy Lambda Layers
Deploy the pandas_layer and langchain_layer folder as Lambda layers to reduce the size of deployment packages


## Replace Your Info

Update the following placeholders in the `./app/app.py` file:

```python
bucket_name = "your_bucket_name"
jobinfo_bucket = "your_jobinfo_bucket"
region = "your_aws_region"
sender = "your_sender_email"
```

`./app/chalicelib/model.py` file:
```python
apiKey="your_apify_key"
```

`./app/chalicelib/helper.py` file:
```python
apify_client="your_apify_client_key"
opeansearch_aws="your_opeansearch_key"
```

## Run Frontend
```python
cd stremlit
streamlit run frontend.py
```

## Team

- **Sophia Luan**
  - GitHub: [@sophialuan](https://github.com/sophialuan)
  - LinkedIn: (https://www.linkedin.com/in/sophia-luan-256354208/)

- **Joyce Qu**
  - GitHub: [@joycequ196](https://github.com/joycequ196))
  - LinkedIn: (https://www.linkedin.com/in/joyce-yuqing-qu-a37097100/)
