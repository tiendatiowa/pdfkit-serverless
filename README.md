# pdfkit-serverless

This project is a serverless function that converts HTML text to PDF using `Pdfkit` (and essentially using `wkhtmltopdf`).
The reason I created this project is because: 1) I could not find any existing example of a serverless with `Pdfkit` (or
`wkhtmltopdf`); and 2) It's not an easy task to figure out how to put `wkhtmltopdf` onto AWS lamda environment. After several
hours of searching, I eventually come across [yumda](https://github.com/lambci/yumda), which is a life-saver for me.
Not only that `yumda` has `wkhtmltopdf` pre-compiled for AWS lamda environments (and many other useful libraries),
but it also have an excellent instruction on how to package your dependencies for deploying to AWS lamda.

## Environment

- Python3.7
- SAM CLI, version 0.43.0

If you have not done so, following the steps to install 
the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
on your local machine. Also recommend installing Docker to test code locally.

## Important note: must modify template.yaml for local testing vs. deployment

Because of a known issue with `sam` [link](https://github.com/awslabs/aws-sam-cli/issues/477), in local you will need to
use the `dependencies` folder, and for deployment you'll need to use the `dependencies.zip`. Comment out the line that
you don't need in this section:

```
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
#      ContentUri: dependencies/ # for local development and testing
      ContentUri: dependencies.zip # for deployment
```

In this project, I've included the version of `wkhtmltopdf` that works at the time of this writing (Mar 23, 2020),
but if you need to update `wkhtmltopdf`, feel free to do so. For example, if using `yumda`, essentially this is what you need:

```
rm -rf dependencies
mkdir dependencies
docker run --rm -v "$PWD"/dependencies:/lambda/opt lambci/yumda:2 yum install -y wkhtmltopdf
```

Then create the zip file:

```
rm dependencies.zip
cd dependencies
zip -yr ../dependencies.zip .
cd ..
```

## Execute the code locally

In your console, execute:

`sam build`

to build the code, then execute:

`sam local invoke -e events/event.json`

to test the code locally. Note that you'll need to modify the event.json file to
use the correct S3 bucket with the right permissions (so that the lamda function can write the output PDF to it).
If your event.json is correct, you'll see a result like this in  the console:

```
$ sam local invoke -e events/event.json 
Invoking app.lambda_handler (python3.7)
DependenciesLayer is a local Layer in the template
Building image...
Requested to skip pulling images ...

Mounting /Users/datnguyen/works/tiendatiowa/sam/pdfkit-serverless/.aws-sam/build/PdfkitFunction as /var/task:ro,delegated inside runtime container
START RequestId: a10bce20-3bed-1d81-7dfb-3b2361d3d3b9 Version: $LATEST
Loading pages (1/6)
[>                                                           ] 0%
[======>                                                     ] 10%
[==============================>                             ] 50%
[============================================================] 100%
Counting pages (2/6)                                               
[============================================================] Object 1 of 1
Resolving links (4/6)                                                       
[============================================================] Object 1 of 1
Loading headers and footers (5/6)                                           
Printing pages (6/6)
[>                                                           ] Preparing
[============================================================] Page 1 of 1
Done                                                                      
END RequestId: a10bce20-3bed-1d81-7dfb-3b2361d3d3b9
REPORT RequestId: a10bce20-3bed-1d81-7dfb-3b2361d3d3b9	Init Duration: 475.22 ms	Duration: 640.24 ms	Billed Duration: 700 ms	Memory Size: 128 MB	Max Memory Used: 40 MB	

{"statusCode":200,"body":"{\"message\": \"Convert HTML to PDF successfully, pdfContent size = 5604\", \"response\": {\"ResponseMetadata\": {\"RequestId\": \"8FF5DFA8E149B580\", \"HostId\": \"R2bDb3baiMMMbHaZKXMGhkeS9bjwICiUmMuHOxjQFWJG4vco7s1XbRNRoinsJD8KPqHzJf/LeUU=\", \"HTTPStatusCode\": 200, \"HTTPHeaders\": {\"x-amz-id-2\": \"R2bDb3baiMMMbHaZKXMGhkeS9bjwICiUmMuHOxjQFWJG4vco7s1XbRNRoinsJD8KPqHzJf/LeUU=\", \"x-amz-request-id\": \"8FF5DFA8E149B580\", \"date\": \"Mon, 23 Mar 2020 21:49:10 GMT\", \"x-amz-version-id\": \"l9S9p3GJJ2kJzgQKzn0MtwmkOG4eNPfX\", \"etag\": \"\\\"b1fdd021db768b3dd57fc412813c035d\\\"\", \"content-length\": \"0\", \"server\": \"AmazonS3\"}, \"RetryAttempts\": 1}, \"ETag\": \"\\\"b1fdd021db768b3dd57fc412813c035d\\\"\", \"VersionId\": \"l9S9p3GJJ2kJzgQKzn0MtwmkOG4eNPfX\"}}"}
```

If you open the S3 bucket, you should see the output file there.

## Deploy the code to AWS

In your console, execute:

`sam deploy --guided`

and follow the guided instruction to deploy the serverless function to AWS.

After deploying successfully, you should see a result like this:

```
CloudFormation outputs from deployed stack
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Outputs                                                                                                                                                                                                     
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Key                 PdfkitApi                                                                                                                                                                               
Description         API Gateway endpoint URL for Prod stage for Pdfkit function                                                                                                                             
Value               https://kj8i85dm88.execute-api.us-east-1.amazonaws.com/Prod/pdfkit/                                                                                                                     

Key                 PdfkitFunction                                                                                                                                                                          
Description         Pdfkit Lambda Function ARN                                                                                                                                                              
Value               arn:aws:lambda:us-east-1:297921772393:function:pdfkit-sls-PdfkitFunction-1B8HOXL2N0124                                                                                                  

Key                 PdfkitFunctionIamRole                                                                                                                                                                   
Description         Implicit IAM Role created for Pdfkit function                                                                                                                                           
Value               arn:aws:iam::297921772393:role/pdfkit-sls-PdfkitFunctionRole-1AK1UC9Q65U3U                                                                                                              
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Successfully created/updated stack - pdfkit-sls in us-east-1
```

Notice the function name `pdfkit-sls-PdfkitFunction-1B8HOXL2N0124` in the log above. You can then test the function using this command:

```
$ aws lambda invoke --function-name pdfkit-sls-PdfkitFunction-1B8HOXL2N0124 --payload <event in base64 format> out
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```

Note the "StatusCode" is 200 even if the function returns error, so to check for the return of the function, run:

```
$ cat out
```

You'll either see the success message (with code 200), or any error that the function encounters (e.g. invalid input, unable to write to S3),
similarly to when running it locally via `sam local invoke`.
If the return code is 200, you will see the result PDF in your bucket.
