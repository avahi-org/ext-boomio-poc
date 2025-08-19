import re
import json
from src.adapters.bedrock_adapter import BedrockAdapter
from src.models.payload import Payload
from src.utils.common_options import (
    GUIDE_PROMPT,
    GEN_IMG_PROMPT
)
from src.utils.helper_function import clean_filename_for_bedrock
from src.config import Config
from fastapi import UploadFile
from typing import List


class MainCore:
    def __init__(self, logger):
        self.logger = logger
        self.bedrock_adapter = BedrockAdapter(logger=logger)

    async def build_conversation(
        self,
        guide_prompt: str,
        files: List[UploadFile]
    ):
        content = [
            {"text": guide_prompt}
        ]
        self.logger.info(f"File list size: {len(files)}")
        if files:
            try:
                for file in files:
                    file_data = await file.read()
                    self.logger.info(f"Read bytes from {file.filename}...")

                    if not file_data or len(file_data) == 0:
                        continue

                    content.append({
                        "document": {
                            "format": file.filename.split(".")[-1].lower(),  # Ej: pdf, docx
                            "name": clean_filename_for_bedrock(
                                filename=file.filename
                            ),
                            "source": {"bytes": file_data}
                        }
                    })
            except Exception as e:
                raise RuntimeError(f"Failed processing files in conversation: {e}")


        return [{
            "role": "user",
            "content": content
        }]

    async def get_recommendation(self, payload: Payload, files: List[UploadFile]):

        try:

            guide_prompt = GUIDE_PROMPT
            self.logger.info(f"Input prompt: {guide_prompt}")
            conversation = await self.build_conversation(
                guide_prompt=guide_prompt,
                files=files
            )
            self.logger.info(f"Conversation: {conversation}")
            response_output = self.bedrock_adapter.invoke_converse(
                payload=conversation
            )
            self.logger.info(f"Model Response: {response_output}")
            ### 2ND STEP, IMG PROMPT GEN
            gen_img_prompt = GEN_IMG_PROMPT
            self.logger.info(f"img generation prompt: {gen_img_prompt}")
            character_prompt = [
                {
                    "role": "user",
                    "content": [
                        {"text": response_output},
                        {"text": f"Based on the information provided, generate a prompt for image generating 2D main character inside the describe game background. Character name inside ** **. Plain text"},
                ],}
            ]
            self.logger.info(f"Conversation: {character_prompt}")
            response_image_prompt = self.bedrock_adapter.invoke_converse(
                payload=character_prompt
            )
            self.logger.info(f"Model Response: {response_image_prompt}")
            ####
            s3_key=self.bedrock_adapter.gen_image(
                payload=response_image_prompt
            )
            ####Final output
            final_json={"guide":response_output,
                       "character_prompt":response_image_prompt,
                       "image_location":f"s3://{Config.BUCKET_NAME}/{s3_key}"}
            parsed_json_output = json.dumps(final_json)
            return parsed_json_output
        except RuntimeError as re:
            raise re
        except Exception as e:
            raise e
