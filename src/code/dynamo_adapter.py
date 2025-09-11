import boto3
import json
from datetime import datetime

class DynamoAdapter:
    def __init__(self, logger, table_name):
        self.logger = logger
        self.dynamodb = self._build_dynamodb()
        self.chat_table = self._get_table(table_name=table_name)

    def _build_dynamodb(self):
        self.logger.info("Inside DynamoAdapter._build_dynamodb()")
        try:
            dynamodb = boto3.resource(
                "dynamodb",
                region_name='eu-central-1'
            )
            return dynamodb
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def _get_table(self, table_name):
        self.logger.info("Inside DynamoAdapter._get_table")
        try:
            table = self.dynamodb.Table(table_name)
            self.chat_table = table
            return table
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def save_chat_history_record(self, bucket_id : str, prompt: str):
        self.logger.info("Inside DynamoAdapter.save_chat_history_record()")
        try:
            now = datetime.now()
            response = self.chat_table.put_item(
                Item={
                    "bucket_id": bucket_id,
                    "prompt": prompt,
                    "timestamp": str(now)
                }
            )
            self.logger.info(f"prompt registry saved: {response}")
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def retrieve_chat_history_record(self, event_id: str):
        self.logger.info("Inside DynamoAdapter.retrieve_chat_history_record()")
        try:
            response = self.chat_table.get_item(
                Key={
                    "event_id": event_id
                }
            )
            self.logger.info(f"Chat history saved: {response}")
            return json.dumps(response.get('Item'))
        except Exception as e:
            self.logger.error(f"Error: {e}")