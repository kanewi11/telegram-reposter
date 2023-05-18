from sqlalchemy import Column, Integer, String, Boolean

from .base import Base


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    dir_path = Column(String, nullable=False)
    posted = Column(Boolean, nullable=False, default=False)
    from_ = Column(String, nullable=False)

    def __init__(self, dir_path: str, from_: str) -> None:
        self.dir_path = dir_path
        self.posted = False
        self.from_ = from_

    def __repr__(self):
        return self.dir_path
