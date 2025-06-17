from pydantic import BaseModel


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str
