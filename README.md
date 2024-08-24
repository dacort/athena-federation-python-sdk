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

## Testing Connector Locally Using Docker

You can test your Lambda function locally using Lambda Docker images.
Note that you must have a Docker daemon running on your machine.
You can test it by calling the CLI:

### Verifying Docker is running

```shell
docker ps
```

### Logging in to Docker

You will need an account on, e.g., [Docker Hub](https://hub.docker.com).

```shell
sudo docker login
# username
# password
```

### Build Docker Images

First, build our Docker image and run it.

```shell
make docker-build
make docker-detached  # or docker-run for testing
```

Then, we can execute a sample `PingRequest`.

```shell
make lambda-ping
```

```json
{"@type": "PingResponse", "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab", "sourceType": "athena_python_sdk", "capabilities": 23}
```

We can also list schemas.

```shell
make lambda-list-schemas
```

```json
{"@type": "ListSchemasResponse", "catalogName": "athena_python_sdk", "schemas": ["sampledb"], "requestType": "LIST_SCHEMAS"}
```

## Deploying your Lambda function to AWS

### Creating your Lambda function

💁 _Please note these are manual instructions until a [serverless application](https://aws.amazon.com/serverless/serverlessrepo/) can be built._

1. First, let's define some variables we need throughout.

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

1. Create an ECR repository for this image

```shell
aws ecr create-repository --repository-name athena_example --image-scanning-configuration scanOnPush=true
```

1. Push tag the image with the repo name and push it up

```shell
docker tag local/athena-python-example ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG}
aws ecr get-login-password | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG}
```

1. Create an IAM role that will allow your Lambda function to execute

_Note the `Arn` of the role that's returned_

```shell
aws iam create-role \
    --role-name athena-example-execution-role \
    --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
aws iam attach-role-policy \
    --role-name athena-example-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

1. Grant the IAM role access to your S3 bucket

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

1. Now create your function pointing to the created repository image

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

### Connect with Athena

1. Choose "Data sources" on the top navigation bar in the Athena console and then click "Connect data source"

1. Choose the Lambda function you just created and click `Connect`!

### Updating the Lambda function

If you update the Lambda function, re-run the build and push steps (updating the `IMAGE_TAG` variable) and then update the Lambda function:

```shell
aws lambda update-function-code \
    --function-name athena-python-example \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/athena_example:${IMAGE_TAG}
```

## Local Development

This version now uses Poetry for dependency management.
Everything is accessible via a Makefile.

### Run Tests

```shell
make # test (with coverage)
```

### Build and Install

```shell
make install
```

### Linting

```shell
make lint
```

### Run tests continuously

```shell
make watch
```

### Push `athena_federation` to PyPI

```shell
make publish
```
