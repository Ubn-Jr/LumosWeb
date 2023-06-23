import pytest
import os

from LumosWeb.api import API
from LumosWeb.orm import Database, Table, Column, ForeignKey

@pytest.fixture
def api():
    return API()


@pytest.fixture
def client(api):
    return api.test_session()

@pytest.fixture
def db():
    DB_PATH = "./test.db"
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = Database(DB_PATH)
    return db


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author


@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    return Book