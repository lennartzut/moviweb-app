import os
from flask import Flask, flash, render_template, request, \
    redirect, url_for
from sqlalchemy.orm import joinedload
from api import make_api_request
from datamanager import Movie, User, SQLiteDataManager
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
app.secret_key = os.getenv('SECRET_KEY')
data_manager = SQLiteDataManager("moviweb.db")


@app.route('/')
def home():
    """
    Render the home page.

    Returns:
        str: HTML for the home page.
    """
    return render_template('home.html')


@app.route('/users', methods=['GET'])
def list_users():
    """
    Display a list of all users.

    Returns:
        str: HTML for the users list.
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Add a new user based on form input.

    Returns:
        Response: Redirect to the users list page.
    """
    user_name = request.form.get("name").strip()
    if not user_name:
        flash("Name is required to add a user.", "danger")
        return redirect(url_for('list_users'))

    # Check if the user already exists
    session = data_manager.Session()
    try:
        existing_user = session.query(User).filter(User.name.ilike(user_name)).first()
        if existing_user:
            flash(f"User '{user_name}' already exists. Please "
                  f"choose a different name.", "danger")
            return redirect(url_for('list_users'))

        # Add new user
        data_manager.add_user(user_name)
        flash(f"User '{user_name}' added successfully.", "success")
        return redirect(url_for('list_users'))
    finally:
        session.close()


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """
    Delete a specific user from the database.

    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        Response: Redirect to the user list page.
    """
    session = data_manager.Session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('list_users'))

        session.delete(user)
        session.commit()
        flash(f"User '{user.name}' deleted successfully.", "success")
    except Exception as e:
        flash(f"An error occurred while trying to delete user: {e}", "danger")
        session.rollback()
    finally:
        session.close()

    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    """
    Display movies for a specific user.

    Args:
        user_id (int): User's ID.

    Returns:
        str: HTML page with user movies or error.
    """
    session = data_manager.Session()
    try:
        user = session.query(User).options(
            joinedload(User.movies)).filter(User.id == user_id).first()
        if not user:
            return render_template('error.html',
                                   message="User not found"), 404
        return render_template('user_movies.html', user=user,
                               movies=user.movies, api_key=API_KEY)
    finally:
        session.close()


@app.route('/users/<int:user_id>/add_movie', methods=['POST'])
def add_movie_form(user_id):
    """
    Add a new movie to the user's list.

    Args:
        user_id (int): User's ID.

    Returns:
        Response: Redirect to user's movie list.
    """
    session = data_manager.Session()
    try:
        user = session.query(User).options(
            joinedload(User.movies)).filter(User.id == user_id).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('list_users'))

        title = request.form.get("title")
        if not title:
            flash("Title is required to add a movie.", "danger")
            return redirect(url_for('user_movies', user_id=user_id))

        movie_data = make_api_request(title)
        if movie_data and movie_data.get("Response") == "True":
            formatted_title = movie_data.get("Title", "Unknown").title()
            director = movie_data.get("Director", "Unknown")
            year = movie_data.get("Year", "Unknown")
            rating = movie_data.get("imdbRating", None)
            imdb_id = movie_data.get("imdbID", None)

            existing_movie = session.query(Movie).filter(
                Movie.user_id == user_id,
                (Movie.imdb_id == imdb_id) |
                (Movie.name.ilike(formatted_title))).first()

            if existing_movie:
                flash(f"The movie '{formatted_title}' is already in your list.",
                      "danger")
                return redirect(url_for('user_movies', user_id=user_id))

            year = int(year) if year.isdigit() else None
            try:
                rating = float(rating) if rating else None
            except ValueError:
                rating = None

            data_manager.add_movie(user_id, formatted_title,
                                   director, year, rating, imdb_id)
            flash(f"Movie '{formatted_title}' added successfully.",
                  "success")
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            flash(f"Movie '{title}' not found in OMDb.", "danger")
            return redirect(url_for('user_movies', user_id=user_id))
    finally:
        session.close()


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>',
           methods=['POST'])
def update_movie(user_id, movie_id):
    """
    Update an existing movie in the user's list.

    Args:
        user_id (int): User's ID.
        movie_id (int): Movie's ID.

    Returns:
        Response: Redirect to user's movie list.
    """
    session = data_manager.Session()
    try:
        user = session.query(User).options(
            joinedload(User.movies)).filter(User.id == user_id).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('list_users'))

        movie = next((m for m in user.movies if m.id == movie_id), None)
        if not movie:
            flash("Movie not found.", "danger")
            return redirect(url_for('user_movies', user_id=user_id))

        title = request.form.get("title")
        director = request.form.get("director")
        year = request.form.get("year")
        rating = request.form.get("rating")

        if title:
            movie.name = title
        if director:
            movie.director = director
        if year:
            try:
                movie.year = int(year)
            except ValueError:
                flash("Invalid year value.", "danger")
                return redirect(url_for('user_movies', user_id=user_id))

        if rating:
            try:
                rating = float(rating)
                if not 1.0 <= rating <= 10.0:
                    raise ValueError("Rating must be between 1.0 and 10.0.")
                movie.rating = rating
            except ValueError:
                flash("Rating must be a decimal between 1.0 and 10.0.",
                      "danger")
                return redirect(url_for('user_movies', user_id=user_id))

        session.commit()
        flash(f"Movie '{movie.name}' updated successfully.", "success")
        return redirect(url_for('user_movies', user_id=user_id))
    finally:
        session.close()


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>',
           methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Delete a movie from the user's list.

    Args:
        user_id (int): User's ID.
        movie_id (int): Movie's ID.

    Returns:
        Response: Redirect to user's movie list.
    """
    session = data_manager.Session()
    try:
        movie = session.query(Movie).filter(
            Movie.id == movie_id, Movie.user_id == user_id).first()
        if not movie:
            flash("Movie not found.", "danger")
            return redirect(url_for('user_movies', user_id=user_id))

        session.delete(movie)
        session.commit()
        flash(f"Movie '{movie.name}' deleted successfully.", "success")
        return redirect(url_for('user_movies', user_id=user_id))
    finally:
        session.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
