
import boto3
from chalice import Chalice, Response

app = Chalice(app_name='smarthire-demo')

_SUPPORTED_DOC_EXTENSIONS = (
    '.pdf'
)

s3_client = boto3.client('s3')
bucket_name = 'sopresumebucket'

def _is_pdf(key):
    return key.endswith(_SUPPORTED_DOC_EXTENSIONS)

#run helper.py
def run_opensearch_import():
    from chalicelib import helper
    print("Run job info fun")
    titles = ["Data Analyst", "Data Engineer", "Data Scientist", "Software Developer", "Product Manager", "Digital Marketer"]
    locations = {"w+CAIQICIHVG9yb250bw==": "Toronto", "w+CAIQICIJVmFuY291dmVy": "Vancourver",
                  "w+CAIQICIITW9udHJlYWw=": "Montreal", "w+CAIQICIHQ2FsZ2FyeQ==": "Calgary", "w+CAIQICIIRWRtb250b24=": "Edmonton"}
    positions = helper.getApiInfo(job_titles=titles,locations=locations)
    _ = helper.connectOpeanSearch(position_df=positions)
    return {"status":"success"}

'''
#send result to email
def send_email(result):
    # Initialize SES client
    ses_client = boto3.client('ses', region_name='us-west-2')  # Change region if needed

    # Email parameters
    sender = 'sophialuanfx@gmail.com'
    recipient = 'sophialuanfx@gmail.com'
    subject = 'Apify Job Result'
    body = f'The Apify Job Result Update to OpeanSearch: {result}'

    # Send email
    response = ses_client.send_email(
        Source=sender,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    print("Email sent:", response)
'''

#run model.py
def get_resume_sum(key, content):
    from chalicelib import model
    print("Run resume Summary")
    result=model.resumeSum( userName=key, resume= content)
    print(result)
    """
    secondResult=model.resuemJobMatch(resume_summary=result, job_path="./raw_google_1129.csv",)
    print("Finished summary. And here is top 5 matched jobs: ")
    print(secondResult)
    """
    return {"result": result}


@app.schedule('cron(0 10 ? * SUN *)')  # Run each sunday at 10am
def opensearch_handler(event):
    result = run_opensearch_import()
    #send_email(result)
    return result


@app.on_s3_event(bucket=bucket_name,
                 events=['s3:ObjectCreated:*'])
def handle_object_update(event):
    import os
    if _is_pdf(key=event.key):     
        #download object from s3
        filepath = '/tmp/' + os.path.basename(event.key)  
        s3_client.download_file(event.bucket, event.key, filepath)  

        #handel resume summary
        result=get_resume_sum(key=event.key, content=filepath)
        os.remove(filepath)
        return Response(body=result, status_code=200)

    
@app.route('/upload', methods=['POST'])
def upload():
    import base64
    try:
        request_data = app.current_request.json_body
        original_filename = request_data['filename']
        encoded_content = request_data['content']
        
        # Decode Base64 content
        file_content = base64.b64decode(encoded_content)
        # Upload file to S3
        s3_client.put_object(Bucket=bucket_name, Key=original_filename, Body=file_content)

        return Response(body={'message': f'File {original_filename} uploaded successfully'}, status_code=200)
    except Exception as e:
        # Log the error for debugging purposes
        app.log.error(f"Error uploading file: {e}")
        return Response(body={'error': 'Error uploading file. Please try again.'}, status_code=500)


