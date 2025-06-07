from app.database.database import Base


class Topic(Base):
    id: int
    name: str
    description: str
    category: str
    difficulty: str
    constraint: str
    duration: int  # in minutes
    repetitions: int = 0  # number of times the topic should be repeated
    sets: int = 0  # number of sets for the topic

    class Config:
        orm_mode = True