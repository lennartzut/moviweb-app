import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')


def make_api_request(movie_title):
    """
    Request movie data from OMDb API.

    Args:
        movie_title (str): The title of the movie.

    Returns:
        dict: JSON response with movie data or None if there's an error.
    """
    if not API_KEY:
        print("Error: API_KEY is not set. Please check your .env file.")
        return None

    api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={movie_title}"
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print("Error:", response.status_code, response.json())
            return None
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Try again later.")
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to OMDb API. "
              "Check your internet connection.")
    except requests.exceptions.RequestException as e:
        print("Error:", e)
    return None
