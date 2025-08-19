import os


class Config:
    AWS_REGION = os.getenv("REGION_NAME")
    KNOWLEDGE_ID = os.getenv("KNOWLEDGE_ID")
    MODEL_ID = os.getenv("MODEL_ID")
    MODEL_ID_GEN_IMAGE = os.getenv("MODEL_ID_GEN_IMAGE")
    TABLE_NAME = os.getenv("TABLE_NAME")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    PREFIX = os.getenv("PREFIX")

    @classmethod
    def set_aws_region(cls, region):
        os.environ['AWS_REGION'] = region

    @classmethod
    def get_aws_region(cls):
        return os.getenv('AWS_REGION', None)
