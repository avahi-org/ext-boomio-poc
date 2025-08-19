import logging
import json
from botocore.exceptions import ClientError
from typing import List

class S3Client:
    """
    A client for interacting with AWS S3, providing methods for common S3 operations.
    """

    def __init__(self, session, bucket_name: str):
        """
        Initialize the S3Client class.

        Args:
            session (boto3.session.Session): Boto3 session to use for creating S3 client and resource.
            bucket_name (str): The name of the S3 bucket to interact with.
        """
        self.bucket_name = bucket_name
        self.s3_resource = session.resource('s3')
        self.s3_client = session.client('s3')
        self.bucket = self.s3_resource.Bucket(bucket_name)

    def check_if_file_exists(self, key: str) -> bool:
        """
        Check if a file exists in the S3 bucket.

        Args:
            key (str): The S3 object key.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        objs = list(self.bucket.objects.filter(Prefix=key))
        return any(obj.key == key for obj in objs)

    def get_file(self, key: str) -> bytes:
        """
        Get a file from S3.

        Args:
            key (str): The S3 object key.

        Returns:
            bytes: The content of the file.

        Raises:
            Exception: If there is an error getting the file from S3.
        """
        try:
            s3_response_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            s3_object = s3_response_object['Body'].read()
            logging.info(f"Got file from s3://{self.bucket_name}/{key}.")
            return s3_object
        except ClientError as e:
            logging.error(f"Error getting file from S3: {e}")
            raise

    def upload_file(self, file_content: bytes, key: str):
        """
        Upload a file to an S3 bucket.

        Args:
            file_content (bytes): File content to upload.
            key (str): S3 object key.

        Raises:
            ClientError: If there is an error uploading the file to S3.
        """
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=file_content, ContentType="image/png" )
            logging.info(f"Uploaded {key} to bucket {self.bucket_name}.")
        except ClientError as e:
            logging.error(f"Error uploading {key} to S3: {e}")
            raise

    def list_objects_with_prefix(self, prefix: str) -> List[str]:
        """
        List all objects in the S3 bucket that start with the given prefix.

        Args:
            prefix (str): The file prefix (e.g. 'data/') to filter by.

        Returns:
            List[str]: A list of object keys that match the given prefix.
        """
        matching_objects = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if key.startswith(prefix):
                        matching_objects.append(key)

        logging.info(f"Found {len(matching_objects)} objects in s3://{self.bucket_name}/ with prefix '{prefix}'.")
        return matching_objects
    
    def list_directories_in_prefix(self, prefix: str) -> List[str]:
        """
        List all immediate sub-directories (common prefixes) under a given prefix in the S3 bucket.
        
        Args:
            prefix (str): The "folder" prefix to look under (e.g. 'inference/').

        Returns:
            List[str]: A list of directory prefixes found under the given prefix.
        """
        directories = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter='/')

        for page in page_iterator:
            if 'CommonPrefixes' in page:
                for cp in page['CommonPrefixes']:
                    directories.append(cp['Prefix'])

        logging.info(f"Found {len(directories)} directories in s3://{self.bucket_name}/{prefix}.")
        return directories