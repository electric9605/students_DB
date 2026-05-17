from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import get_db  # ← Импортируем get_db отсюда
from models import User

# текущего пользователя по user_id из заголовка
def get_current_user_by_id(
    user_id: int = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или не активен",
        )
    return user

# пользователь может быть анонимным
def get_optional_user_by_id(
    user_id: Optional[int] = Header(None, alias="X-User-ID"),
    db: Session = Depends(lambda: None)
) -> Optional[User]:
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()