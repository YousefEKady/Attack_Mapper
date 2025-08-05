from pydantic import BaseModel, Field
from typing import List

class ScanRequest(BaseModel):
    domain: str
    scans: List[str] = Field(default_factory=lambda: ["all"])
