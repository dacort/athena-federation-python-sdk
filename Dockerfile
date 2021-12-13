FROM python:3.8-slim AS build

# Set our workdir
WORKDIR /app

# Get ready to build
RUN pip install build

# Now copy the app over and build a wheel
COPY src /app/src
COPY pyproject.toml setup.cfg /app/
RUN python -m build

## Now use the compiled wheel in our lambda function
FROM amazon/aws-lambda-python:3.8.2021.12.09.15 AS lambda

ENV TARGET_BUCKET=replace_me

COPY --from=build /app/dist/unoffical_athena_federation_sdk-*-py3-none-any.whl /
RUN pip install /unoffical_athena_federation_sdk-*-py3-none-any.whl

COPY example/ ./
RUN ls ./

CMD [ "handler.lambda_handler" ]
