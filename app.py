
import boto3

from chalice import Chalice
from chalicelib import model
from chalicelib import helper

app = Chalice(app_name='smarthire-demo')

_SUPPORTED_DOC_EXTENSIONS = (
    '.pdf'
)

s3Client = boto3.client('s3')

def _is_pdf(key):
    return key.endswith(_SUPPORTED_DOC_EXTENSIONS)

def get_resume_sum(key, path):
    print("Run resume Summary")
    #file= s3Client.Bucket(bucket).download_file(key)
    result=model.resumeSum( userName=key, resumePath= path)
    print(result)
    secondResult=model.resuemJobMatch(resume_summary=result, job_path="no")
    print("Finished summary. And here is top 5 matched jobs: ")
    print(secondResult)

#get_resume_sum('sopresumebukcet', 'Sophia_Resume.pdf')
helper.getApiInfo()

@app.lambda_function()
def opeansearch_import():
        print("Run job info fun")
        helper.getApiInfo()
        print("Job Info saved")


@app.on_s3_event(bucket='sopresumebucket',
                 events=['s3:ObjectCreated:*'])
def handle_object_update(event):
    print ('file uploading')
    print("The variable, basics is of type:", type(event.key))
    
    if _is_pdf(key=event.key):
        print(f'Received event for bucket: {event.bucket}, key: {event.key}')
        filepath = '/tmp/' + event.key
        s3Client.download_file(event.bucket, event.key, filepath)
        #response = s3Client.get_object(Bucket=event.bucket, Key=event.key)
        print(f"Download file from bucket: {event.bucket}")
        
        #get_resume_sum( key=event.key, path=event.key)
        get_resume_sum( key=event.key, path=filepath)
        
       
    print ('file uploaded')



