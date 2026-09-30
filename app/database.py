"""Database engine, session factory and FastAPI dependency."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://cities:cities@localhost:5432/cities",
)


def _normalize_database_url(url: str) -> str:
    """Rewrite a legacy PostgreSQL scheme to the psycopg 3 dialect.

    Render hands out connection strings as ``postgres://user:pass@host:5432/db``.
    SQLAlchemy maps that bare scheme to the **psycopg2** dialect, which is not
    installed, so ``create_engine`` would fail at import time. Local compose
    already supplies ``postgresql+psycopg://…``. This function rewrites only
    the scheme prefix (``postgres://`` or ``postgresql://`` becomes
    ``postgresql+psycopg://``) and passes everything else through untouched.

    The query string is deliberately left alone: the SSL-mode query parameter
    is never read, stripped, or appended. psycopg 3 inherits libpq's default
    "prefer" SSL behaviour, which negotiates SSL against Render's managed
    Postgres and falls back to plain TCP against the local container, whose
    Postgres runs without SSL. Forcing SSL to be required would break local
    development, so only the scheme prefix is ever rewritten.
    """
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


engine = create_engine(_normalize_database_url(DATABASE_URL), pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base holding the model metadata."""


def get_db():
    """Yield a database session and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
