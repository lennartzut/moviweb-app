import requests
from unittest.mock import patch
from api import make_api_request


def mock_requests_get_success(*args, **kwargs):
    """
    Mocks a successful response from OMDb API.
    """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if "&i=" in args[0]:
        return MockResponse(
            {
                "Response": "True",
                "Title": "The Godfather",
                "Year": "1972",
                "Director": "Francis Ford Coppola"
            },
            200
        )
    return MockResponse(
        {
            "Response": "True",
            "Search": [
                {
                    "Title": "The Godfather",
                    "Year": "1972",
                    "imdbID": "tt0068646"
                }
            ]
        },
        200
    )


def mock_requests_get_failure(*args, **kwargs):
    """
    Mocks a failed response from OMDb API.
    """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse(
        {"Response": "False", "Error": "Movie not found"},
        200
    )


def mock_requests_get_error(*args, **kwargs):
    """
    Mocks an error response from OMDb API.
    """
    raise requests.exceptions.RequestException("API request failed")


@patch('requests.get', side_effect=mock_requests_get_success)
def test_make_api_request_success(mock_get):
    """
    Tests successful API request for title and IMDb ID.
    """
    response = make_api_request("The Godfather")
    assert response is not None
    assert len(response) == 1
    assert response[0]['Title'] == "The Godfather"

    response = make_api_request("tt0068646", by_id=True)
    assert response is not None
    assert response['Title'] == "The Godfather"
    assert response['Director'] == "Francis Ford Coppola"


@patch('requests.get', side_effect=mock_requests_get_failure)
def test_make_api_request_failure(mock_get):
    """
    Tests API request with no results found.
    """
    response = make_api_request("Nonexistent Movie")
    assert response is None


@patch('requests.get', side_effect=mock_requests_get_error)
def test_make_api_request_exception(mock_get):
    """
    Tests API request handling an exception.
    """
    response = make_api_request("The Godfather")
    assert response is None

    response = make_api_request("tt0068646", by_id=True)
    assert response is None
