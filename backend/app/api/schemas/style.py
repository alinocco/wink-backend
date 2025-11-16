from pydantic import BaseModel
from typing import List, Optional


class StyleOption(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class StylesResponse(BaseModel):
    styles: List[StyleOption]

