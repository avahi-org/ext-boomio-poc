from pydantic import BaseModel
from src.utils.helper_function import as_form


@as_form
class Payload(BaseModel):
    event_id: str
