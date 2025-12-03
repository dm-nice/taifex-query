from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class FetchResult(BaseModel):
    module: str
    date: str
    status: str = Field(..., pattern="^(success|fail|error)$")
    summary: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    source: str = "TAIFEX"
    error: Optional[str] = None

class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, date: str) -> dict:
        """
        Fetch data for the given date.
        Must return a dictionary that satisfies the FetchResult model,
        or better yet, return a FetchResult.model_dump().
        """
        pass
