from data_models import db, Book, Author
from sqlalchemy import or_


def search_books(search_query=None):
    # Start with the base query selecting all books
    books_with_authors_query = db.session.query(Book, Author).join(Author)

    # Apply search filtering if a search_query is provided
    if search_query:
        books_with_authors_query = books_with_authors_query.filter(
            or_(Book.title.ilike(f"%{search_query}%"), Author.name.ilike(f"%{search_query}%"))
        )
    # Execute the query and return the results
    return books_with_authors_query.all()


def sort_search_results(results, sort_by):
    # Apply sorting to the search results if sort_by is provided
    if sort_by == 'title':
        results.sort(key=lambda x: x[0].title)
    elif sort_by == 'author':
        results.sort(key=lambda x: x[1].name)
    elif sort_by == 'publication_year':
        results.sort(key=lambda x: x[0].publication_year)

    return results
