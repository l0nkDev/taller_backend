from pydantic import BaseModel
from typing import List


class ParsedOrderItem(BaseModel):
    dish_id: int
    name: str
    quantity: int


class AIOrderResponse(BaseModel):
    transcription: str
    items: List[ParsedOrderItem]
