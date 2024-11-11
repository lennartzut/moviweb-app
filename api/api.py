import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

def make_api_request(movie_title):
    """Make an API request to OMDb API with the provided movie title."""
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
        print("Error: The request timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to the OMDb API. Please check your internet connection.")
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
