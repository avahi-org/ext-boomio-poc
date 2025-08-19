import logging

from fastapi import APIRouter, File, UploadFile, Depends
from typing import List, Optional

from src.models.payload import Payload
from src.cores.main_core import MainCore
from src.utils.helper_function import create_json_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()


class MainController:
    def __init__(self):
        self.logger = logger
        self.core = MainCore(logger=logger)

    async def get_recomendation(
            self,
            payload: Payload,
            files: List[UploadFile]
    ):
        if payload.event_id == '':
            return create_json_response(status_code=200, response={
                "guide": "",
                "character_prompt": "",
                "image_location": ""
            })

        self.logger.info(f"Payload: {payload}")
        try:
            response = await self.core.get_recommendation(
                payload=payload,
                files=files
            )
            return create_json_response(status_code=200, response=response)
        except RuntimeError as re:
            self.logger.error(f"Error: {re}")
            return create_json_response(status_code=500, response={'Error': re})



controller = MainController()

@router.post("/recommedation")
async def get_recommendation(
    payload: Payload = Depends(Payload.as_form),
    files: List[UploadFile] = File(...)
):
    return await controller.get_recomendation(payload=payload, files=files)
