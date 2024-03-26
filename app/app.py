
import boto3
from chalice import Chalice



app = Chalice(app_name='smarthire-demo')

_SUPPORTED_DOC_EXTENSIONS = (
    '.pdf'
)

s3Client = boto3.client('s3')

def _is_pdf(key):
    return key.endswith(_SUPPORTED_DOC_EXTENSIONS)


@app.lambda_function()
def opensearch_import(event, context):
    from chalicelib import helper
    print("Run job info fun")
    helper.getApiInfo()
    print("Job Info saved")


@app.on_s3_event(bucket='sopresumebucket',
                 events=['s3:ObjectCreated:*'])
def handle_object_update(event):
    import os
    if _is_pdf(key=event.key):
#        s3_object = s3Client.get_object(Bucket=event.bucket, Key=event.key)
#        resume_content = s3_object['Body'].read()
#        get_resume_sum(key=event.key, content=resume_content)
        filepath = '/tmp/' + os.path.basename(event.key)  
        s3Client.download_file(event.bucket, event.key, filepath)  
        get_resume_sum(key=event.key, content=filepath)
        os.remove(filepath)

def get_resume_sum(key, content):
    from chalicelib import model
    print("Run resume Summary")
    result=model.resumeSum( userName=key, resume= content)
    print(result)
    secondResult=model.resuemJobMatch(resume_summary=result, job_path="no")
    print("Finished summary. And here is top 5 matched jobs: ")
    print(secondResult)

#get_resume_sum('sopresumebukcet', './data/Sophia_Resume.pdf')
#helper.getApiInfo()