from typing import Optional

from pydantic import BaseModel


class ApproveDraftRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None
