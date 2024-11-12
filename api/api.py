import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

def make_api_request(query, by_id=False):
    """
    Request movie data from OMDb API based on title or IMDb ID.

    Args:
        query (str): The title keyword or IMDb ID to search for.
        by_id (bool): If True, searches using IMDb ID.
                      If False, searches by title.

    Returns:
        dict: JSON response with movie data or None if there's an error.
    """
    if not API_KEY:
        print("Error: API_KEY is not set. Please check your .env file.")
        return None

    # Adjust the URL based on whether we are searching by title or IMDb ID
    if by_id:
        api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&i={query}"
    else:
        api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&s={query}"

    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == requests.codes.ok:
            data = response.json()
            if data.get("Response") == "True":
                # If by_id is True, return the full movie data directly
                if by_id:
                    return data
                # Otherwise, return the list of search results
                return data.get("Search", [])
            else:
                print("No results found:", data.get("Error"))
                return None
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
