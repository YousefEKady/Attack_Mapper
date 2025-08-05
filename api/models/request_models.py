from pydantic import BaseModel
from typing import List, Optional

class ScanRequest(BaseModel):
    domain: str
    scans: Optional[List[str]] = ["all"]
