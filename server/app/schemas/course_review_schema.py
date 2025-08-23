from typing import Optional

from pydantic import BaseModel


class ApproveDraftRequest(BaseModel):
    approved: Optional[bool] = True
    feedback: Optional[str] = None
