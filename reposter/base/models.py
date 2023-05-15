import traceback
from pathlib import Path

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import exc

from reposter.logger import logger


Base = declarative_base()

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR.joinpath('telegram.db')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)


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


def add_post(dir_path: str, from_: str) -> None:
    with Session() as session:
        try:
            task = session.query(Post).filter(Post.dir_path == dir_path).first()
            if not task:
                task = Post(dir_path=dir_path, from_=from_)
                session.add(task)
                session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
            logger.error(traceback.format_exc())


def get_new_posts(from_: str = 'telegram') -> list:
    posts = []
    with Session() as session:
        try:
            posts = session.query(Post).filter(Post.posted == False,
                                               Post.from_ == from_).all()
        except exc.SQLAlchemyError:
            session.rollback()
            logger.error(traceback.format_exc())
    return posts


def posted(dir_path: str) -> None:
    with Session() as session:
        try:
            task = session.query(Post).filter(Post.dir_path == dir_path).first()
            if task:
                task.posted = True
                session.commit()
        except exc.SQLAlchemyError as error:
            session.rollback()
            logger.error(traceback.format_exc())
            raise error


Base.metadata.create_all(engine)
