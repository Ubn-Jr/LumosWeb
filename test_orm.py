import sqlite3

def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []

def test_define_tables(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"

def test_create_tables(db, Author, Book):
    db.create(Author)
    db.create(Book)

    assert Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    assert Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in  ("author", "book"):
        assert table in db.tables

def test_create_author_instance(db, Author):
    db.create(Author)
    author = Author(name="J. K. Rowling", age=54)
    assert author.name == "J. K. Rowling"
    assert author.age == 54
    assert author.id is None

def test_save_author_instance(db, Author):
    db.create(Author)

    rowling = Author(name="J. K. Rowling", age=54)  # instance of Author class
    db.save(rowling)

    assert rowling._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [54, "J. K. Rowling"]
    )
    assert rowling.id == 1

    man = Author(name="Man Harsh", age=20)
    db.save(man)
    assert man.id == 2

    vik = Author(name="Vik Star", age=43)
    db.save(vik)
    assert vik.id == 3

    jack = Author(name="Jack Sparrow", age=34)
    db.save(jack)
    assert jack.id == 4

def test_query_all_authors(db, Author):
    db.create(Author)
    rowling = Author(name="J. K. Rowling", age=54)
    vik = Author(name="Vik Star", age=43)
    db.save(rowling)
    db.save(vik)

    authors = db.all(Author)

    assert Author._get_select_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"]
    )
    assert len(authors) == 2
    assert type(authors[0]) == Author
    assert {a.age for a in authors} == {54, 43}
    assert {a.name for a in authors} == {"J. K. Rowling", "Vik Star"}

def test_get_author(db, Author):
    db.create(Author)
    
    novel = Author(name="J. K. Rowling", age=54)
    db.save(novel)

    rowling_from_db = db.get(Author, id=1)

    assert Author._get_select_where_sql(id=1) == (
        "SELECT id, age, name FROM author WHERE id = ?;",
        ["id", "age", "name"],
        [1]
    )
    assert rowling_from_db.name == "J. K. Rowling"
    assert rowling_from_db.age == 54
    assert rowling_from_db.id == 1
    assert type(rowling_from_db) == Author

def test_get_book(db, Author, Book):
    db.create(Author)
    db.create(Book)

    rowling = Author(name="J. K. Rowling", age=54)
    db.save(rowling)

    harry_potter = Book(title="Harry Potter", published=True, author=rowling)
    db.save(harry_potter)

    book_from_db = db.get(Book, 1)

    assert book_from_db.title == "Harry Potter"
    assert book_from_db.published == True
    assert book_from_db.author.name == "J. K. Rowling"
    assert book_from_db.author.age == 54
    assert book_from_db.author.id == 1
    assert type(book_from_db) == Book

def test_query_all_books(db, Author, Book):
    db.create(Author)
    db.create(Book)

    rowling = Author(name="J. K. Rowling", age=54)
    db.save(rowling)

    harry_potter = Book(title="Harry Potter", published=True, author=rowling)
    db.save(harry_potter)

    books = db.all(Book)

    assert len(books) == 1
    assert books[0].title == "Harry Potter"
    assert books[0].published == True
    assert books[0].author.name == "J. K. Rowling"
    assert books[0].author.age == 54
    assert books[0].author.id == 1
    assert type(books[0]) == Book