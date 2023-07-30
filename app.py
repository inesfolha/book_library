import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from data_models import db, Author, Book
from helpers.api_endpoint import search_hapi_books, get_isbn_code
from helpers.helper_functions import search_books, sort_search_results
from my_custom_exceptions import APICallError

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE")
app.secret_key = os.getenv("SECRETKEY")

# Add cascade='all, delete-orphan' to enable deleting all associated books when deleting an author
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Add a new author to the library.

    Returns:
        If the request method is POST and the author is added successfully,
        the user will see a success message on the 'add_author.html' page.
        If the request method is POST and there are errors in adding the author,
        the user will see an error message on the 'add_author.html' page.
        If the request method is GET, the user will see the 'add_author.html' page.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        date_of_death_str = request.form.get('date_of_death')

        if not name or not birth_date_str:
            # Handle missing name or birth date
            error_message = 'Please provide both name and birth date.'
            return render_template('add_author.html', error_message=error_message)

        # Check if the birth date has the correct format
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            error_message = 'Invalid birth date format. Please use YYYY-MM-DD format for dates.'
            return render_template('add_author.html', error_message=error_message)

        # Check if the date_of_death has the correct format
        date_of_death = None
        if date_of_death_str:
            try:
                date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date()
            except ValueError:
                error_message = 'Invalid date of death format. Please use YYYY-MM-DD format for dates.'
                return render_template('add_author.html', error_message=error_message)

        try:
            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            return render_template('add_author.html', message='Author added successfully!')

        except SQLAlchemyError as e:
            # Handle database-related errors
            error_message = 'An unexpected error occurred. Please try again later.'
            return render_template('add_author.html', error_message=error_message)

    # For GET requests, render the 'add_author.html' page
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Add a new book to the library.

    POST Method:
    If the form data is valid, the book is added to the database, and a success message is displayed.
    If there are missing fields or an invalid publication year format, an error message is shown.

    GET Method:
    The 'add_book.html' page is rendered with a dropdown list of authors.

    Returns:
        For successful book addition (POST), a success message is displayed.
        For errors (POST) or the 'add_book.html' page (GET), appropriate messages or template is returned.
    """
    authors = Author.query.all()

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        # Check for missing fields
        if not isbn or not title or not publication_year or not author_id:
            error_message = 'Please provide all required fields.'
            return render_template('add_book.html', error_message=error_message, authors=authors)

        # Check for invalid year format
        if not publication_year.isdigit() or len(publication_year) != 4:
            error_message = 'Invalid publication year format. Please provide a valid year.'
            return render_template('add_book.html', error_message=error_message, authors=authors)

        # Convert publication year to an integer
        publication_year = int(publication_year)

        try:
            # Create a new Book record in the database
            new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
            db.session.add(new_book)
            db.session.commit()

            return render_template('add_book.html', message='Book added successfully!', authors=authors)

        except SQLAlchemyError as e:
            # Handle database-related errors
            error_message = 'An unexpected error occurred. Please try again later.'
            return render_template('add_book.html', error_message=error_message, authors=authors)

    return render_template('add_book.html', authors=authors)


@app.route('/', methods=['GET', 'POST'])
def home():
    """Display the home page with a list of books.

    If a search query is provided, filter the books based on the search query.
    If a sorting option is provided, sort the books accordingly.

    Returns:
        If there are books matching the search query, they are displayed on the 'home.html' page.
        If there are no matching books, a message indicating no results is shown.
    """

    sort_by = request.args.get('sort')
    search_query = request.form.get('search_query')

    success_messages = get_flashed_messages(category_filter=['success'])
    error_messages = get_flashed_messages(category_filter=['error'])
    try:
        books_with_authors = search_books(search_query)
    except SQLAlchemyError:
        # Handle database-related errors
        error_message = 'An unexpected error occurred while accessing the database. Please try again later.'
        return render_template('error.html', error_code=500, message=error_message), 500

    # Handle other errors
    if books_with_authors is None:
        error_message = 'An unexpected error occurred. Please try again later.'
        return render_template('error.html', error_code=500, message=error_message), 500

    if not books_with_authors:
        message = 'No books found that match the search criteria.'
    else:
        if search_query:
            message = f'Search results for "{search_query}":'
        else:
            message = 'All books:'

    if sort_by:
        books_with_authors = sort_search_results(books_with_authors, sort_by)

    return render_template('home.html', books_with_authors=books_with_authors, message=message,
                           success_message=success_messages, error_message=error_messages)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book from the library.

        Args:
            book_id (int): The ID of the book to be deleted.

        Returns:
            After deleting the book, the user is redirected to the home page.
        """
    book = Book.query.get_or_404(book_id)
    if not book:
        # Book with the given book_id not found
        error_message = 'Book not found.'
        flash(error_message, 'error')
        return redirect(url_for('home'))

    # Get the author of the book
    author = Author.query.get(book.author_id)
    try:
        # Delete the book from the database
        db.session.delete(book)

        # Check if the author has any other books in the library
        other_books_by_author = Book.query.filter_by(author_id=author.id).filter(Book.id != book_id).count()

        if other_books_by_author == 0:
            # If the author has no other books, delete the author from the database
            db.session.delete(author)

        db.session.commit()

        message = f'The book "{book.title}" by {author.name} has been successfully deleted.'
        flash(message, 'success')
        return redirect(url_for('home'))

    except SQLAlchemyError as e:
        # Handle database-related errors
        db.session.rollback()  # Roll back the transaction
        error_message = 'An unexpected error occurred while accessing the database. Please try again later.'
        app.logger.exception(e)
        flash(error_message, 'error')
        return redirect(url_for('home'))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """Delete an author and all associated books from the database.

    Args:
        author_id (int): The ID of the author to be deleted.

    Returns:
        Response: A redirect response to the home page.

    Raises:
        NoResultFound: If the author with the given ID does not exist in the database.
    """
    try:
        author = Author.query.get_or_404(author_id)
        books = Book.query.filter_by(author_id=author_id).all()

        # Delete all books associated with the author
        for book in books:
            db.session.delete(book)

        db.session.delete(author)
        db.session.commit()

        message = f'The author "{author.name}" and all associated books have been successfully deleted.'
        flash(message, 'success')
        return redirect(url_for('home'))

    except NoResultFound:
        # Handle the case when the author with the given ID does not exist
        flash('Author not found.', 'error')
        return redirect(url_for('home'))

    except SQLAlchemyError as e:
        # Handle database-related errors
        db.session.rollback()  # Roll back the session to avoid inconsistent data
        flash('An error occurred while deleting the author and associated books.', 'error')
        # Log the error for further investigation if needed
        app.logger.exception(e)
        return redirect(url_for('home'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
        Search for books using the API interface based on user input.

        Returns:
            GET: Renders the 'search_new_book.html' template to display the search form.
            POST: Redirects to the 'search_new_book.html' template with search results on success.
                  Displays an error message on API-related errors or unexpected errors.
        """
    if request.method == 'POST':
        try:
            search_query = request.form['search_query']

            # Search for the book using the API interface
            title, publication_year, authors, cover, additional_info = search_hapi_books(search_query)

            isbn = get_isbn_code(title, authors)

            # Pass the retrieved data to the template
            return render_template('search_new_book.html', title=title, publication_year=publication_year,
                                   authors=authors, cover=cover, additional_info=additional_info, isbn=isbn)
        except APICallError as e:
            # Handle API-related errors
            flash(str(e), 'error')
            return render_template('search_new_book.html')

        except Exception as e:
            # Catch-all for unexpected errors, log and display a generic error message
            app.logger.exception(e)
            flash('An unexpected error occurred while processing your request.', 'error')
            return render_template('search_new_book.html')

    return render_template('search_new_book.html')


@app.route('/book/<int:book_id>')
def book_details(book_id):
    """
       Display details of a specific book and its corresponding author.

       Args:
           book_id (int): The ID of the book to display details for.

       Returns:
           Renders the 'book_details.html' template with book and author details on success.
           Displays an error message on unexpected database errors.
       """
    try:
        messages = get_flashed_messages(category_filter=['success'])
        # Query the Book table to get the book and its corresponding author
        book = Book.query.get_or_404(book_id)
        # Get the author of the book
        author = Author.query.get(book.author_id)

        return render_template('book_details.html', book=book, author=author, success_message=messages)

    except SQLAlchemyError as e:
        app.logger.exception(e)
        flash('An unexpected error occurred while processing your request.', 'error')
        return render_template('book_details.html.html')


@app.route('/book/<int:book_id>/update', methods=['GET', 'POST'])
def update_book(book_id):
    """
    Update book details based on user input.

    Args:
        book_id (int): The ID of the book to be updated.

    Returns:
        GET: Renders 'update_book.html' with book and author details.
        POST: Redirects to the book details page on success, or re-renders the page on error.
    """
    book = Book.query.get_or_404(book_id)
    author = Author.query.get(book.author_id)

    if request.method == 'POST':
        try:
            publication_year = request.form['publication_year']
            rating = request.form['rating']

            if publication_year and not publication_year.isdigit() and len(publication_year) != 4:
                raise ValueError("Publication year must be numeric.")
            if rating and not rating.isdigit():
                raise ValueError("Rating must be numeric.")

            book.title = request.form['title']

            # Handle date fields if there is input
            if publication_year:
                book.publication_year = int(publication_year)
            else:
                book.publication_year = None

            author.name = request.form['authors']

            # Handle birth_date if there is input
            birth_date_str = request.form['birth_date']
            if birth_date_str:
                author.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            else:
                author.birth_date = None

            # Handle death_date if there is input
            death_date_str = request.form['death_date']
            if death_date_str:
                author.death_date = datetime.strptime(death_date_str, '%Y-%m-%d').date()
            else:
                author.death_date = None

            book.isbn = request.form['isbn']

            # Handle rating if there is input
            if rating:
                book.rating = int(rating)
            else:
                book.rating = None

            book.cover = request.form['cover']
            book.additional_info = request.form['additional_info']

            db.session.commit()

            flash('Book details have been updated successfully!', 'success')
            return redirect(url_for('book_details', book_id=book.id))

        except ValueError as e:
            # Handle form validation errors
            flash(str(e), 'error')
            return redirect(url_for('book_details', book_id=book.id))

        except SQLAlchemyError as e:
            # Handle SQLAlchemy-related database errors
            app.logger.exception(e)
            flash('An unexpected database error occurred while updating the book details.', 'error')
            return redirect(url_for('book_details', book_id=book.id))

    return render_template('update_book.html', book=book, author=author)


@app.route('/search/add_book', methods=['POST'])
def add_searched_data():
    """
       Add a new book to the library based on searched data.

       Returns:
           POST: Redirects to the 'home' page on success or error.
       """
    if request.method == 'POST':
        try:
            isbn = request.form['isbn']
            title = request.form['title']
            publication_year = request.form['publication_year']
            authors_str = request.form['authors']
            cover = request.form['cover']
            additional_info = request.form['additional_info']

            # Check if the author already exists in the database
            existing_author = Author.query.filter_by(name=authors_str).first()

            if existing_author:
                # If the author exists, use the existing author ID
                author_id = existing_author.id
            else:
                # If the author does not exist, create a new author record
                new_author = Author(name=authors_str)
                db.session.add(new_author)
                db.session.commit()
                author_id = new_author.id

            # Create a new Book record in the database
            new_book = Book(isbn=isbn, title=title, publication_year=publication_year,
                            author_id=author_id, cover=cover, additional_info=additional_info)
            db.session.add(new_book)
            db.session.commit()

            message = f'The book "{title}" has been successfully added to the library'
            flash(message, 'success')
            return redirect(url_for('home'))

        except SQLAlchemyError as e:
            # Handle SQLAlchemy-related database errors
            app.logger.exception(e)
            flash('An unexpected database error occurred while adding the book to the library.', 'error')

    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal Server Error"), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message="Forbidden"), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
