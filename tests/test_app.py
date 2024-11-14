import pytest
from app import app, data_manager
from flask import url_for
from bs4 import BeautifulSoup
from datamanager.sqlite_data_manager import Base, User, Movie

@pytest.fixture
def client():
    """
    Provides a Flask test client for making requests to the app.
    """
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_database():
    """
    Sets up the database for testing and tears it down after.
    """
    Base.metadata.drop_all(bind=data_manager.engine)
    Base.metadata.create_all(bind=data_manager.engine)
    yield
    Base.metadata.drop_all(bind=data_manager.engine)

def extract_flash_message(response):
    """
    Utility function to extract flash messages from response data.
    """
    soup = BeautifulSoup(response.data, 'html.parser')
    messages = soup.find_all("div", class_="alert")
    return [message.text.strip().replace("\n×", "").strip()
            for message in messages]

def test_home_page(client):
    """
    Tests the response status code and checks page content.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"MoviWeb App" in response.data

def test_list_users(client):
    """
    Tests the users list page and checks for correct content.
    """
    response = client.get('/users')
    assert response.status_code == 200
    assert b"List of Users" in response.data

def test_add_user(client):
    """
    Tests adding a user, including validation and duplication.
    """
    response = client.post('/add_user',
                           data={'name': 'John Doe'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "User 'John Doe' added successfully." in extract_flash_message(
        response)

    response = client.post('/add_user',
                           data={'name': ''},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "Name is required to add a user." in extract_flash_message(
        response)

    response = client.post('/add_user',
                           data={'name': 'John Doe'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "User 'John Doe' already exists. Please choose a different name."\
           in extract_flash_message(response)

def test_delete_user(client):
    """
    Tests deleting an existing user and handling user not found.
    """
    client.post('/add_user', data={'name': 'John Doe'})
    session = data_manager.Session()
    user = session.query(User).filter_by(name='John Doe').first()
    assert user is not None
    user_id = user.id
    session.close()

    response = client.post(f'/users/{user_id}/delete',
                           follow_redirects=True)
    assert response.status_code == 200
    assert "User 'John Doe' deleted successfully." in extract_flash_message(
        response)

    session = data_manager.Session()
    user = session.query(User).filter_by(name='John Doe').first()
    assert user is None
    session.close()

def test_user_movies(client):
    """
    Tests displaying the list of movies for a user.
    """
    client.post('/add_user', data={'name': 'John Doe'})
    session = data_manager.Session()
    user = session.query(User).filter_by(name='John Doe').first()
    user_id = user.id
    session.close()

    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    assert b"Movie Collection" in response.data

def test_add_movie(client):
    """
    Tests adding a movie to a user's movie collection.
    """
    client.post('/add_user', data={'name': 'John Doe'})
    session = data_manager.Session()
    user = session.query(User).filter_by(name='John Doe').first()
    user_id = user.id
    session.close()

    response = client.get(url_for('add_movie_form', user_id=user_id)
                          + '?title=The Godfather')
    assert response.status_code == 200

    response = client.post(url_for('confirm_add_movie', user_id=user_id),
                           data={'imdb_ids': ['tt0068646']},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "Movies 'The Godfather' added successfully." in extract_flash_message(
        response)

def test_update_movie(client):
    """
    Tests updating details of a movie in the user's collection.
    """
    client.post('/add_user', data={'name': 'John Doe'})
    session = data_manager.Session()
    user = session.query(User).filter_by(name='John Doe').first()
    user_id = user.id
    session.close()

    client.post(url_for('confirm_add_movie', user_id=user_id),
                data={'imdb_ids': ['tt0068646']},
                follow_redirects=True)

    session = data_manager.Session()
    movie = session.query(Movie).filter_by(
        user_id=user_id, imdb_id='tt0068646').first()
    movie_id = movie.id
    session.close()

    response = client.post(f'/users/{user_id}/update_movie/{movie_id}',
                           data={'title': 'The Godfather Updated',
                                 'director': 'Francis Ford Coppola',
                                 'year': '1972',
                                 'rating': '9.2'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "Movie 'The Godfather Updated' updated successfully." in extract_flash_message(
        response)

def test_delete_movie(client):
    """
    Tests deleting a movie from a user's movie collection.
    """
    client.post('/add_user', data={'name': 'John Doe'})
    session = data_manager.Session()
    user = session.query(User).filter_by(name='John Doe').first()
    user_id = user.id
    session.close()

    client.post(url_for('confirm_add_movie', user_id=user_id),
                data={'imdb_ids': ['tt0068646']},
                follow_redirects=True)

    session = data_manager.Session()
    movie = session.query(Movie).filter_by(
        user_id=user_id, imdb_id='tt0068646').first()
    movie_id = movie.id
    session.close()

    response = client.post(f'/users/{user_id}/delete_movie/{movie_id}',
                           follow_redirects=True)
    assert response.status_code == 200
    assert f"Movie '{movie.name}' deleted successfully." in extract_flash_message(
        response)

def test_get_movie_plot(client):
    """
    Tests retrieving the plot of a movie from the API.
    """
    response = client.get('/get_movie_plot/tt0068646')
    assert response.status_code == 200
    assert b"plot" in response.data
