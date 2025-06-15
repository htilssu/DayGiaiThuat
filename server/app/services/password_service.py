from fastapi import HTTPException
from app.database.database import get_db
from app.models.user_model import User
from app.utils.utils import password_hash


class PasswordService:
    def __init__(self):
        self.db = get_db()

    def __del__(self):
        self.db.close()

    def change_password(self, user_id: int, new_password: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password = password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user
