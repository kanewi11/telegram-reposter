from sqlalchemy.future import select

from reposter.database.models import Post
from reposter.database.base import get_async_session, async_session


async def async_add_post(dir_path: str, from_: str) -> None:
    async with get_async_session() as session:
        stmt = select(Post).where(Post.dir_path == dir_path, Post.from_ == from_)
        results = await session.execute(stmt)
        post = results.scalars().first()
        if post:
            return

        new_post = Post(dir_path=dir_path, from_=from_)
        session.add(new_post)


async def async_get_new_posts(from_: str = 'telegram') -> list:
    async with async_session() as session:
        stmt = select(Post).where(Post.posted == False, Post.from_ == from_)
        results = await session.execute(stmt)
        return results.scalars().fetchall()


async def async_posted(dir_path: str) -> None:
    async with get_async_session() as session:
        stmt = select(Post).where(Post.dir_path == dir_path)
        results = await session.execute(stmt)
        posts = results.scalars().all()
        for post in posts:
            post.posted = True
