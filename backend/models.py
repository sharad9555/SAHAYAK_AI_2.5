from datetime import datetime
from sqlalchemy import String,Text,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .database import Base
class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100))
    phone:Mapped[str|None]=mapped_column(String(20),nullable=True)
    assistance_type:Mapped[str|None]=mapped_column(String(60),nullable=True)
    history:Mapped[list["History"]]=relationship(back_populates="user",cascade="all, delete-orphan")
class History(Base):
    __tablename__="history"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    question:Mapped[str]=mapped_column(Text)
    answer:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    user:Mapped["User"]=relationship(back_populates="history")
