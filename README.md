# Book Library
<p id="top"></p>

## Introduction                                     
The Book Library is a web application built with Flask that allows users to manage a library's collection of books and authors. 

Users can add new authors and books, search for books, view book details, update book information, and delete books and authors. 

Additionally, the system integrates with external APIs to search for book information and automatically add new books to the library.

## Table of Contents
- [Introduction](#introduction)
- [Description](#description)
  - [Project Structure](#project-structure)
  - [App Features](#app-features)
  - [Data Models](#data-models)
  - [API Integration](#api-integration)
  - [Error Handling](#error-handling)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [How does it work?](#how-does-it-work)
  - [Watch demo](https://www.youtube.com/watch?v=QfXVmT3e1SQ)
- [Limitations](#limitations)
- [Contributions](#contributions)

[Back to the Top](#top)

## Description

### Project Structure
The project follows a structured directory layout:

 - **.data:** Contains the SQLite database file (library.sqlite). 


 - **.helpers:** Contains utility modules for API integration and helper functions. 


 - **.static:** Stores static files, such as CSS styles. 


 - **.templates:** Contains HTML templates for rendering pages. 


 - **app.py:** The main application script. 


 - **data_models.py:** Defines the database models for authors and books using SQLAlchemy. 


 - **my_custom_exceptions.py:** Defines custom exceptions for handling errors. 


 - **requirements.txt:** Lists the required Python packages. 


 - **README.md:** This documentation file.


[Back to the Top](#top)
### App Features
1. **Author Management**
   - Add new authors with details such as name, birth date, and date of death (optional).
   - Authors are automatically associated with their respective books.
2. **Book Management**
   - Add new books with information including ISBN, title, publication year, and author selection. 
   - View and edit book details, including cover images and additional information. 
   - Delete books individually, which may also delete the associated author if they have no other books in the library.
3. **Search and Sort**
   - Search for books in the library by title, author, or any keyword.
   - Sort books by title, author name, or publication year.
4. **External API Integration**
   - Retrieve book information from external APIs

[Back to the Top](#top)

### Data Models 

The Book Library uses two main data models to store information about authors and books: the Author model and the Book model.

#### Author Model
The Author model represents information about authors, including their name, birth date, and date of death (if applicable). Each author is associated with one or more books in the library.

##### Fields:
- **id:** An integer representing the unique identifier of the author.

- **name:** A string (up to 100 characters) representing the author's name.

- **birth_date:** A date field representing the author's date of birth (nullable).

- **date_of_death:** A date field representing the author's date of death (nullable).

The Author model allows the system to manage information about authors and their relationships with books.

#### Book Model
The Book model represents information about books in the library, including ISBN, title, publication year, author, cover image URL, rating, and additional information.

##### Fields:

- **id:** An integer representing the unique identifier of the book.

- **isbn:** A string (up to 13 characters) representing the ISBN code of the book (nullable).

- **title:** A string (up to 200 characters) representing the title of the book.

- **publication_year:** An integer representing the year the book was published.

- **author_id:** An integer representing the foreign key reference to the associated author.

- **cover:** A string representing the URL of the book's cover image (nullable).

- **rating:** A floating-point number representing the book's rating (nullable).

- **additional_info:** A text field for storing additional information about the book (nullable).

The Book model allows the system to manage detailed information about books, including their ISBN codes, titles, authors, and more. Each book is associated with an author through the author_id field, which establishes a relationship between books and authors in the library.

[Back to the Top](#top)

### API Integration
The application integrates with external APIs for book information retrieval:

[HAPI Books API](https://rapidapi.com/roftcomp-laGmBwlWLm/api/hapi-books): Used to search for books based on user input and retrieve book details.

[Book Finder API](https://rapidapi.com/dfskGT/api/book-finder1): Find book ISBN codes based on title and author.


### Error Handling
The application handles various types of errors, including form validation errors, database-related errors, and API call errors. It provides user-friendly error messages and displays error pages when necessary.

[Back to the Top](#top)
## Installation

### Prerequisites

To run this project, you'll need Python 3 and the following dependencies:

- Flask
- SQLAlchemy
- Requests 
- Dotenv (for environment variable management)

You can install these dependencies using pip:

``` python 
 pip install flask sqlalchemy
 ```

### Installation Steps

1. Clone this repository or download the script file:

```bash
git clone https://github.com/inesfolha/book_library.git
```
If you downloaded a ZIP archive, extract its contents to a directory of your choice.

2. Change to the script's directory:

 ```bash
  cd book_library
```

3. Install the required dependencies:
 ```bash
  pip install -r requirements.txt
```

4. Create the database. Then uncomment lines 35 and 36 from data_models.py and run the script to create the database tables. After the database is set you can delete those lines or comment them out again. 


5. Set up environment variables: Create a .env file in the project directory and add the following variables:
 ```bash
DATABASE=<your_database_uri>
SECRETKEY=<your_secret_key>
API_KEY=<your_api_key>
```
6. To run the script, open your terminal and execute the following command:
```bash
python app.py
```
The application will be accessible at http://localhost:5002 by default.

[Back to the Top](#top)

## How does it work?
 * [Watch Demo](https://www.youtube.com/watch?v=QfXVmT3e1SQ)


## Limitations
- **API Usage Limitations:**
The application relies on external APIs, such as the HAPI Books API and the Book Finder API, for book information retrieval. These APIs have usage limitations on their free plans, including rate limits.  Users are advised to review the API documentation for any usage restrictions and consider upgrading to a paid plan if needed.


- **Local Development Only:**
The application is intended for local development and testing. It may require additional configuration and security measures for deployment to a production server. Users planning to deploy the application in a production environment should ensure proper security and scalability considerations.


- **Limited Error Handling:**
While the application provides error handling for common scenarios, it may not cover all possible error cases. Users are encouraged to contribute to the project by enhancing error handling and providing better user feedback for various situations.


These limitations are important to consider when using the Book Library, and users should be aware of these constraints to make informed decisions regarding its usage and deployment.
[Back to the Top](#top)


## Contributions

Contributions to this project are welcome. If you'd like to contribute, please fork the repository, make your changes, and create a pull request.

[Back to the Top](#top)