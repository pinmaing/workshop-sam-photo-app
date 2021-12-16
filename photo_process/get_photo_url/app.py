import json
import os
import boto3
import base64
from datetime import datetime, timedelta, timezone

def get_photo_url(s3_bucket, s3_signed_url_expiration, 
                  photo_path, s3_region = "ap-northeast-1"):
    offset = timezone(timedelta(hours=+9))
    date = datetime.now(offset)
    dateStr = date.strftime("%Y/%m/%d")
    
    # boto3 Reference : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html
    s3_client = boto3.client("s3", region_name = s3_region)
    key = photo_path
     
    # Reference : https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html
    signed_url = s3_client.generate_presigned_url("get_object", 
                                                  Params={"Bucket": s3_bucket , 
                                                          "Key": key}, 
                                                  ExpiresIn=s3_signed_url_expiration)
    return signed_url

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

def lambda_handler_post(event, context):
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
    s3_signed_url_expiration = os.environ["SIGNED_URL_EXPIRATION"]
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
    # eventPathParameters = json.loads(json.dumps(event))["pathParameters"]
    # photo_path = eventPathParameters["photo_path"]
    # photo_path = event['queryStringParameters']['photo_path']
    eventBody = json.loads(base64.b64decode(event["body"]))
    photo_path = eventBody["photo_path"]

    signed_url = get_photo_url(s3_bucket,s3_signed_url_expiration,
                               photo_path,s3_region)

    body = {
                "message": "Please check Image by this Url with Get Method!",
                "signed_url": signed_url
            }
    return get_response(200,body)

def lambda_handler_get(event, context):
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
    s3_signed_url_expiration = os.environ["SIGNED_URL_EXPIRATION"]
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
    photo_path = event['queryStringParameters']['photo_path']

    signed_url = get_photo_url(s3_bucket,s3_signed_url_expiration,
                               photo_path,s3_region)

    body = {
                "message": "Please check Image by this Url with Get Method!",
                "signed_url": signed_url
            }
    return get_response(200,body)