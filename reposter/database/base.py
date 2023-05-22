import traceback
from pathlib import Path
from typing import ContextManager
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from reposter.logger import logger


BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR.joinpath('posts.db')

DSN = f'sqlite:///{DB_PATH}'

engine = create_engine(DSN, echo=False)

if DSN.startswith('sqlite'):
    DSN = DSN.replace('sqlite', 'sqlite+aiosqlite')

async_engine = create_async_engine(DSN, echo=False)

async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
sync_session = sessionmaker(bind=engine)

Base = declarative_base()


def init_models():
    Base.metadata.create_all(engine)


@asynccontextmanager
async def get_async_session(**kwargs) -> AsyncSession:
    new_session = async_session(**kwargs)
    try:
        yield new_session
        await new_session.commit()
    except Exception:
        await new_session.rollback()
        logger.error(traceback.format_exc())
    finally:
        await new_session.close()


@contextmanager
def get_session(**kwargs) -> ContextManager[Session]:
    new_session = sync_session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        logger.error(traceback.format_exc())
    finally:
        new_session.close()
