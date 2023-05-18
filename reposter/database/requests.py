from sqlalchemy.future import select

from .models import Post
from .base import get_session, sync_session


def add_post(dir_path: str, from_: str) -> None:
    with get_session() as session:
        stmt = select(Post).where(Post.dir_path == dir_path, Post.from_ == from_)
        results = session.execute(stmt)
        post = results.scalars().first()

        if post:
            return

        new_post = Post(dir_path=dir_path, from_=from_)
        session.add(new_post)


def get_new_posts(from_: str = 'telegram') -> list:
    with sync_session() as session:
        stmt = select(Post).where(Post.posted == False, Post.from_ == from_)
        results = session.execute(stmt)
        return results.scalars().fetchall()


def posted(dir_path: str) -> None:
    with get_session() as session:
        stmt = select(Post).where(Post.dir_path == dir_path)
        results = session.execute(stmt)
        posts = results.scalars().all()
        for post in posts:
            post.posted = True
