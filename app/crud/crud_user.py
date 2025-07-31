from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            user_type=obj_in.user_type,
            phone_number=obj_in.phone_number,
            location=obj_in.location,
            bio=obj_in.bio,
            company_name=obj_in.company_name,
            company_website=obj_in.company_website,
            company_size=obj_in.company_size,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def update_last_login(self, db: Session, *, user: User) -> User:
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_employees(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            db.query(self.model)
            .filter(User.user_type == "employee")
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_employers(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            db.query(self.model)
            .filter(User.user_type == "employer")
            .offset(skip)
            .limit(limit)
            .all()
        )


user = CRUDUser(User)
