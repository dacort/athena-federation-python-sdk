# (Unofficial) Python SDK for Athena Federation

This is an _unofficial_ Python SDK for Athena Federation.

## Overview

The Python SDK makes it easy to create new Amazon Athena Data Source Connectors using Python. It is under active development so the API may change from version to version.

You can see an example implementation that [queries Google Sheets using Athena](https://github.com/dacort/athena-gsheets).

![gsheets_example](https://user-images.githubusercontent.com/1512/134044216-f8498ce8-2015-4935-bc95-6f9fd5234a25.png)

### Current Limitations

- Partitions are not supported, so Athena will not parallelize the query using partitions.

## Example Implementations
- [Athena data source connector for Minio](https://github.com/Proximie/athena-connector-for-minio/)

## Local Development

- Ensure you've got the `build` module install and SDK dependencies.

```
pip install build
pip install -r requirements.txt
```

- Now make a wheel.

```shell
python -m build
```

This will create a file in `dist/`: `dist/unoffical_athena_federation_sdk-0.0.0-py3-none-any.whl`

Copy that file to your example repo and you can include it in your `requirements.txt` like so:

```
unoffical-athena-federation-sdk @ file:///unoffical_athena_federation_sdk-0.0.0-py3-none-any.whl
```

## Validating your connector

You can test your Lambda function locally using Lambda Docker images.

First, build our Docker image and run it.

```shell
docker build -t local/athena-python-example .
docker run --rm -p 9000:8080 local/athena-python-example
```

Then, we can execute a sample `PingRequest`.

```shell
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"@type": "PingRequest", "identity": {"id": "UNKNOWN", "principal": "UNKNOWN", "account": "123456789012", "arn": "arn:aws:iam::123456789012:root", "tags": {}, "groups": []}, "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab"}'
```

```json
{"@type": "PingResponse", "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab", "sourceType": "athena_python_sdk", "capabilities": 23}
```

We can also list schemas.

```shell
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"@type": "ListSchemasRequest", "identity": {"id": "UNKNOWN", "principal": "UNKNOWN", "account": "123456789012", "arn": "arn:aws:iam::123456789012:root", "tags": {}, "groups": []}, "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab"}'
```

```json
{"@type": "ListSchemasResponse", "catalogName": "athena_python_sdk", "schemas": ["sampledb"], "requestType": "LIST_SCHEMAS"}
```

## Creating your Lambda function

💁 _Please note these are manual instructions until a [serverless application](https://aws.amazon.com/serverless/serverlessrepo/) can be built._

0. First, let's define some variables we need throughout.

```shell
export SPILL_BUCKET=<BUCKET_NAME>
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1
export IMAGE_TAG=v0.0.1
```

1. Create an S3 bucket that this Lambda function will use for Spill data

```shell
aws s3 mb ${SPILL_BUCKET}
```

2. Create an ECR repository for this image

```shell
aws ecr create-repository --repository-name athena_example --image-scanning-configuration scanOnPush=true
```

3. Push tag the image with the repo name and push it up

```shell
docker tag local/athena-python-example ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG}
aws ecr get-login-password | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG}
```

4. Create an IAM role that will allow your Lambda function to execute

_Note the `Arn` of the role that's returned_

```shell
aws iam create-role \
    --role-name athena-example-execution-role \
    --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
aws iam attach-role-policy \
    --role-name athena-example-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

5. Grant the IAM role access to your S3 bucket

```shell
aws iam create-policy --policy-name athena-example-s3-access --policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::'${SPILL_BUCKET}'"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": ["arn:aws:s3:::'${SPILL_BUCKET}'/*"]
    }
  ]
}'
aws iam attach-role-policy \
    --role-name athena-example-execution-role \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/athena-example-s3-access
```


6. Now create your function pointing to the created repository image

```shell
aws lambda create-function \
    --function-name athena-python-example \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/athena-example-execution-role \
    --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG} \
    --environment 'Variables={TARGET_BUCKET=<BUCKET_NAME>}' \
    --description "Example Python implementation for Athena Federated Queries" \
    --timeout 60 \
    --package-type Image
```

## Connect with Athena!

1. Choose "Data sources" on the top navigation bar in the Athena console and then click "Connect data source"

![](docs/athena_connect.png)

2. Choose the Lambda function you just created and click `Connect`!

![](docs/athena_connect_lambda.png)

## Updating the Lambda function

If you update the Lambda function, re-run the build and push steps (updating the `IMAGE_TAG` variable) and then update the Lambda function:

```shell
aws lambda update-function-code \
    --function-name athena-python-example \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG}
```
