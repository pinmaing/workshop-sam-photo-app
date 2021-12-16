import json
import os
import boto3
from botocore.client import Config
import base64
from datetime import datetime, timedelta, timezone


def get_generate_upload_url(s3_bucket, s3_signed_url_expiration, 
                            attachment_file, s3_region = "ap-northeast-1"):

    offset = timezone(timedelta(hours=+9))
    date = datetime.now(offset)
    dateStr = date.strftime("%Y/%m/%d")
    
    # boto3 Reference : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html
    s3_client = boto3.client("s3", config=Config(signature_version="s3v4"),
                             region_name = s3_region)
    
    # key = s3_object_prefix + "/" + dateStr + "/" + attachment_file
    key = attachment_file
    
    # Reference : https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html
    signed_url = s3_client.generate_presigned_url("put_object", 
                                                  Params={"Bucket": s3_bucket , 
                                                          "Key": key}, 
                                                  ExpiresIn=s3_signed_url_expiration)
    
    return signed_url

def upload_photo(s3_bucket, binary_photo, 
                 photo_name, content_type, s3_region = "ap-northeast-1"):

    offset = timezone(timedelta(hours=+9))
    date = datetime.now(offset)
    dateStr = date.strftime("%Y/%m/%d")
    photoBody = base64.b64decode(binary_photo)
    
    key = dateStr + "/" + photo_name
    
    # Reference : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html
    s3 = boto3.resource('s3', region_name = s3_region)
    bucket = s3.Bucket(s3_bucket)
       
    bucket.put_object(
            ContentType = content_type,
            Body = photoBody,
            Key = key
        )
    
    return key

def get_response(status_code, body):
    # Lambda Response Format for API Gateway Reference 
    # https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
    # Reference : https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": 
                "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": 
                "GET,HEAD,OPTIONS,POST,PATCH,PUT,DELETE",
            "Access-Control-Allow-Origin": 
                "*"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    
    # Get Value from Environment Variable
    s3_bucket = os.environ["S3_BUCKET"]
    # s3_signed_url_expiration = os.environ["SIGNED_URL_EXPIRATION"]
    s3_region = os.environ["S3_REGION"]
    auth_key = os.environ["AUTH_KEY"]
    
    # API Gateway trigger event parameter format Reference
    # https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    authorization = str(event["headers"]["Authorization"])
    if authorization != auth_key:
        body = {
            "message": "Unauthorized!",
            "signed_url": ""
        }
        return get_response(401,body)
    
    # API Gateway trigger event parameter format Reference
    # https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    # eventBody = json.loads(json.dumps(event))["body"]
    # attachment_file =json.loads(eventBody)["attachment_file"]
    
    # signed_url = get_generate_upload_url(s3_bucket,s3_signed_url_expiration,attachment_file)
    # body = {
    #             "message": "Please upload Image by this Url with Put Method!",
    #             "signed_url": signed_url
    #         }
    
    eventBody = event["body"]
    photoName = event['queryStringParameters']['photo_name']
    content_type = (event["headers"]["Content-Type"])
    uploaded_photo_path = upload_photo(s3_bucket,eventBody,photoName,content_type,s3_region)

    body = {
                "message": "Successfully Uploaded!",
                "uploaded_photo_path": uploaded_photo_path
            }
    return get_response(200,body)