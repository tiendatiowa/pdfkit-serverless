import json
import pdfkit
import boto3


class InvalidInput(Exception):
    def __init__(self, message):
        self.message = message


class InvalidPdfContent(Exception):
    def __init__(self, message):
        self.message = message


class UnableToUploadToS3(Exception):
    def __init__(self, message):
        self.message = message


def uploadToS3(bucket, key, body):
    try:
        s3 = boto3.client('s3')
        response = s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=body
        )
        return response
    except:
        raise UnableToUploadToS3("Unable to upload content to S3 bucket '{}' and key '{}'".format(bucket, key))


def extractParamFromJson(event, paramName):
    try:
        return event[paramName]
    except:
        raise InvalidInput("Event doesn't have param with name '{}'".format(paramName))


def lambda_handler(event, context):
    try:
        bodyStr = extractParamFromJson(event, "body")
        bodyJson = json.loads(bodyStr)
        htmlContent = extractParamFromJson(bodyJson, "input")  # the HTML content to write to the output PDF
        if len(htmlContent) == 0:
            raise InvalidInput("There's no content in the 'input' param")

        bucket = extractParamFromJson(bodyJson, "bucket")  # the bucket to write the output PDF
        if len(bucket) == 0:
            raise InvalidInput("The 'bucket' param is empty")

        key = extractParamFromJson(bodyJson, "output")  # the name of the output PDF
        if len(key) == 0:
            raise InvalidInput("The 'output' param is empty")

        pdfContent = pdfkit.from_string(htmlContent, False)
        if len(pdfContent) == 0:
            raise InvalidPdfContent("Could not convert input {} to PDF".format(htmlContent))

        res = uploadToS3(bucket, key, pdfContent)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Convert HTML to PDF successfully, pdfContent size = {}".format(len(pdfContent)),
                "response": res
            }),
        }
    except InvalidInput as ex:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Event is invalid",
                "event": event,
                "exception": ex.message
            })
        }
    except InvalidPdfContent as ex:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Content of URL is invalid",
                "event": event,
                "exception": ex.message
            })
        }
    except UnableToUploadToS3 as ex:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Unable to upload result to S3",
                "event": event,
                "exception": ex.message
            })
        }
    except Exception as ex:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Unable to process event",
                "event": event,
                "exception": str(ex)
            })
        }
