from pydantic import BaseModel


class CreateTopicSchema(BaseModel):
    name: str


class UpdateTopicSchema(BaseModel):
    name: str
