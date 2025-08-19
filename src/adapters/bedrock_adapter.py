import boto3
import time
import json
import re
import random
import base64

from botocore.exceptions import ClientError
from string import Template

from src.config import Config
from src.models.payload import Payload
from s3_client import S3Client

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=Config.get_aws_region()
)
session = boto3.session.Session()
client = S3Client(session, Config.BUCKET_NAME)

class BedrockAdapter:

    def __init__(self, logger):
        self.logger = logger
        self.bedrock_client = bedrock
        self.s3_client = client

    def invoke_converse(self, payload):
        self.logger.info("Inside BedrockAdapter._invoke_model()")
        max_retries = 3
        delay_seconds = 1.5
        for attempt in range(1, max_retries + 1):
            try:
                response = self.bedrock_client.converse(
                modelId=Config.MODEL_ID,
                messages=payload,
                inferenceConfig={"maxTokens": 2048, "temperature": 0.3},
                )
                self.logger.info(f"Initial Response: {response}")
                response_output = response["output"]["message"]["content"][0]["text"]
                # Fix escaped newlines
                response_output = re.sub(r'\\n', '\n', response_output)
                # Fix escaped quotes
                response_output = re.sub(r'\\"', '"', response_output)
                # Fix escaped single quotes
                response_output = re.sub(r"\\'", "'", response_output)
                response_output = re.sub(r'\s+', ' ', response_output).strip()
                #clean_output = re.sub(r"```json|```", "", response_output).strip()
                #parsed_json_output = json.loads(clean_output)
                self.logger.info(f"Model response: {response_output}")
                return response_output
            except ClientError as ce:
                self.logger.error(f"Client Error: {ce}")
                error_code = ce.response['Error']['Code']
                if error_code in ["ThrottlingException", "TooManyRequestsException"]:
                    if attempt < max_retries:
                        time.sleep(delay_seconds**max_retries) # exponential backoff
                        continue  # retry
                    else:
                        raise RuntimeError("Throttling: Retry limit exceeded. Please try again later.")
            except Exception as e:
                self.logger.error(f"Error: {e}")
                raise RuntimeError(f"Unexpected error during model invocation: {e}")

    def gen_image(self, payload):
        self.logger.info("Inside BedrockAdapter._gen_image()")
        max_retries = 3
        delay_seconds = 1.5
        for attempt in range(1, max_retries + 1):
            try:
                # Generate a random seed between 0 and 858,993,459
                seed = random.randint(0, 858993460)
                # Format the request payload using the model's native structure.
                native_request = {
                    "taskType": "TEXT_IMAGE",
                    "textToImageParams": {"text": payload},
                    "imageGenerationConfig": {
                        "seed": seed,
                        "quality": "standard",
                        "height": 512,
                        "width": 512,
                        "numberOfImages": 1,
                    },
                }
                # Convert the native request to JSON.
                request = json.dumps(native_request)
                # Invoke the model with the request.
                response_img_gen = self.bedrock_client.invoke_model(
                modelId=Config.MODEL_ID_GEN_IMAGE,
                body=request
                )
                self.logger.info(f"Initial Response: {response_img_gen}")
                # Decode the response
                model_response = json.loads(response_img_gen["body"].read())
                base64_image_data = model_response["images"][0]
                image_data = base64.b64decode(base64_image_data)
                # -------- Get progressive number from S3 --------
                # List existing objects in bucket with prefix
                existing_objects = self.s3_client.list_objects_with_prefix(prefix=Config.PREFIX)
                
                if existing_objects:
                    # Count existing files to continue sequence
                    file_count = len(existing_objects)+1
                else:
                    file_count = 1
                
                # Define S3 key
                s3_key = f"{Config.PREFIX}{file_count}.png"
                
                # Upload to S3
                self.s3_client.upload_file(key=s3_key, file_content=image_data)
                self.logger.info(f"Image uploaded to s3://{Config.BUCKET_NAME}/{s3_key}")
                return s3_key
            except ClientError as ce:
                self.logger.error(f"Client Error: {ce}")
                error_code = ce.response['Error']['Code']
                if error_code in ["ThrottlingException", "TooManyRequestsException"]:
                    if attempt < max_retries:
                        time.sleep(delay_seconds**max_retries) # exponential backoff
                        continue  # retry
                    else:
                        raise RuntimeError("Throttling: Retry limit exceeded. Please try again later.")
            except Exception as e:
                self.logger.error(f"Error: {e}")
                raise RuntimeError(f"Unexpected error during model invocation: {e}")

