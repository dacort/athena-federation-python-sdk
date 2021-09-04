import os

from athena.federation.lambda_handler import AthenaLambdaHandler
from athena.federation.data_catalog import AthenaDataCatalog

# This needs to be a valid bucket that the Lambda function role has access to
spill_bucket = os.environ['TARGET_BUCKET']

example_handler = AthenaLambdaHandler(
    data_source=AthenaDataCatalog(),
    spill_bucket=spill_bucket
)

def lambda_handler(event, context):
    # For debugging purposes, we print both the event and the response :)
    print(event)
    response = example_handler.process_event(event)
    print(response)

    return response
