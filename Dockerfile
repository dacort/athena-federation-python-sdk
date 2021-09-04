FROM python:3.8-slim AS build

# Set our workdir
WORKDIR /app
RUN mkdir /app/src

# Copy requirements and pip install for great caching
COPY requirements.txt /app/requirements.txt
COPY setup.py /app/setup.py

# Get ready to build
RUN pip install build
RUN pip install -r requirements.txt

# Now copy the app over and build a wheel
COPY . /app
RUN python -m build

## Now use the compiled wheel in our lambda function
FROM public.ecr.aws/lambda/python:3.8 AS lambda

ENV TARGET_BUCKET=replace_me

COPY --from=build /app/dist/unoffical_athena_federation_sdk-0.0.0-py3-none-any.whl /
RUN pip install /unoffical_athena_federation_sdk-0.0.0-py3-none-any.whl

COPY src/handler.py ./
RUN ls ./

CMD [ "handler.lambda_handler" ]