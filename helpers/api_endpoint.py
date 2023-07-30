import requests
import os
import time
from my_custom_exceptions import APICallError
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def search_hapi_books(search):
    try:
        search_query = search.replace(' ', '+')
        url = f"https://hapi-books.p.rapidapi.com/search/{search_query}"

        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "hapi-books.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)

        # Check if the response status code indicates success (2xx)
        response.raise_for_status()

        # Check if the response contains a list of results
        if isinstance(response.json(), list):
            result = response.json()[0]
        else:
            result = response.json()

        if result:
            title = result.get('name')
            additional_info = result.get('url')
            cover = result.get('cover')
            authors = result.get('authors')
            publication_year = result.get('year')
            return title, publication_year, authors, cover, additional_info

    except requests.exceptions.RequestException as e:
        # Handle connection errors or other issues with the API call
        raise APICallError("Error occurred while searching for the book using HAPI Books API.") from e

    except (ValueError, KeyError) as e:
        # Handle JSON parsing errors or missing keys in the response
        raise APICallError("Error occurred while parsing the response from HAPI Books API.") from e

    except Exception as e:
        # Catch-all for any other unexpected errors
        raise APICallError("An unexpected error occurred while searching for the book.") from e


def get_isbn_code(book_title, authors):
    if not isinstance(authors, list):
        authors_list = [authors]
        author_names = ", ".join(authors_list)
    else:
        author_names = ", ".join(authors)

    url = "https://book-finder1.p.rapidapi.com/api/search"

    querystring = {"title": book_title, "author": author_names, "page": "1"}

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "book-finder1.p.rapidapi.com"
    }

    # API limits one request per second
    time.sleep(1)

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Check if the response status code indicates success (2xx)

        result = response.json()
        if "results" in result:
            first_result = result["results"][0]

            # Extract the ISBN from the first result
            isbn_code = first_result.get('published_works', [])[0].get('isbn')
            return isbn_code
        else:
            return ""

    except requests.exceptions.RequestException as e:
        print(e)
        return ""

    except Exception as e:
        print(e)
        return ""

# (search_hapi_books('the little mermaid'))
# title, publication_year, authors, cover, additional_info = search_hapi_books('the little mermaid')
# print(title)
# print(authors)
# print(get_isbn_code(title, authors))

# title, publication_year, authors, cover, additional_info = search_hapi_books('Romeo and Juliet')
# print(title)
# print(authors)
# print(get_isbn_code(title, authors))

# print(get_isbn_code('Romeo and Juliet', 'William Shakespeare'))    #WORKS
# print(get_isbn_code('Murder on the Orient Express', 'Agatha Christie')) #WORKS
# print(get_isbn_code('The Lord of the Rings ', 'J.R.R. Tolkien')) #WORKS
