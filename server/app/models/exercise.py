from app.database.database import Base


class Exercise(Base):
    id: int
    name: str
    description: str
    category: str
    difficulty: str
    constraint: str
    duration: int  # in minutes
    repetitions: int = 0  # number of times the exercise should be repeated
    sets: int = 0  # number of sets for the exercise

    class Config:
        orm_mode = True
