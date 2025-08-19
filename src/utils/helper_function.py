import inspect
import re
import os
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Form
from pydantic import BaseModel
from typing import Type, Any, Optional



def create_json_response(status_code: int, response: dict) -> JSONResponse:
    """
    Creates a JSON response with a given status code and response dictionary.
    """
    json_encode_response = jsonable_encoder(response)
    return JSONResponse(
        content=json_encode_response,
        media_type="application/json",
        status_code=status_code
    )

def as_form(cls: Type[BaseModel]):
    """
    Translate a pydatic BaseModel to a Form(...) object from fastapi
    to be able to get the payload elements in the multipart/form-data
    request.
    """
    new_params = []

    for field_name, model_field in cls.__fields__.items():
        annotation = model_field.annotation
        default = Form(...) if model_field.is_required() else Form(model_field.default)

        new_params.append(
            inspect.Parameter(
                field_name,
                inspect.Parameter.POSITIONAL_ONLY,
                default=default,
                annotation=annotation
            )
        )

    async def _as_form(**data: Any) -> BaseModel:
        return cls(**data)

    sig = inspect.signature(_as_form)
    _as_form.__signature__ = sig.replace(parameters=new_params)  # type: ignore
    setattr(cls, 'as_form', _as_form)
    return cls

def clean_filename_for_bedrock(filename: str, prefix: Optional[str] = None, max_length: int = 60) -> str:
    name, _ = os.path.splitext(filename)

    name = re.sub(r"[a-f0-9]{8,}", "", name)
    name = re.sub(r"\d{8,}", "", name)

    name = name.replace("_", " ")

    name = re.sub(r"[^\w\s\-\(\)\[\]]", "", name)

    name = re.sub(r"\s{2,}", " ", name)

    name = name.strip()

    if prefix:
        name = f"{prefix} - {name}"

    if len(name) > max_length:
        name = name[:max_length].rstrip() + "..."

    return name
