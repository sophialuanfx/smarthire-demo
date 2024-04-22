
import os
import boto3
from chalice import Chalice, Response

app = Chalice(app_name='smarthire-demo')
s3_client = boto3.client('s3')

#replace with your own information
bucket_name = ''
jobinfo_bucket=''
region=''
sender=''


_SUPPORTED_DOC_EXTENSIONS = (
    '.pdf'
)
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
    s3_client.put_object(Bucket=jobinfo_bucket, Key='raw_google_1129.csv', Body=positions.to_csv(index=False))
    _ = helper.connectOpeanSearch(position_df=positions)
    return {"status":"success"}

#send email each time second result printed
def send_email(email, body):
    ses_client = boto3.client('ses', region_name=region)
    sender_email = sender
    email_subject = "Weekly Job Matching Results"
    bodys="Here are the top 5 matched jobs:\n" + body

    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': email_subject},
                'Body': {'Text': {'Data': bodys}}
            }
        )
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


#run model.py
def get_resume_sum(key, content):
    from chalicelib import model
    print("Run resume Summary")
    result=model.resumeSum( userName=key, resume= content)
    print(result)
    secondResult=model.resuemJobMatch(resume_summary=result, job_path='./data/raw_google_1129.csv', locations=[])
    print("Finished summary. And here is top 5 matched jobs: ")
    print(secondResult)
    print("Successful! Sending email..")

    recipient_email = sender
    email_body = str(secondResult)
    send_email(recipient_email, email_body)

#get_resume_sum('sophia',"./data/Sophia_resume.pdf")

#3
@app.schedule('cron(0 10 ? * SUN *)')  # Run each sunday at 10am
def opensearch_handler(event):
    result = run_opensearch_import()
    return result

#2
@app.on_s3_event(bucket=bucket_name,
                 events=['s3:ObjectCreated:*'])
def handle_object_update(event):
    if _is_pdf(key=event.key):     
        #download object from s3
        filepath = '/tmp/' + os.path.basename(event.key)  
        s3_client.download_file(event.bucket, event.key, filepath)  

        #handel resume summary
        results=get_resume_sum(key=event.key, content=filepath)
        os.remove(filepath)
        return Response(body=results, status_code=200)

#1
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


