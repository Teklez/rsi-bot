from sqlalchemy.orm import Session
from ..models.user import User

def get_or_create_user(db: Session, tg_user):
    user = db.query(User).filter(User.telegram_id == tg_user.id).first()
    if not user:
        user = User(telegram_id=tg_user.id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
