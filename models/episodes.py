from typing import List, Optional
from pydantic import BaseModel

class Episode(BaseModel):
    name: str = ""
    path: str = ""
    size: int = 0
    unit: str = "B"
    download_time: str = ""

class Episodes(BaseModel):
    episodes: Optional[List[Episode]] = list()
    total_size: float = 0
    unit: str = "B"