from flask import Flask, request, jsonify, redirect, url_for
from sqlalchemy.orm import joinedload
from datamanager import User, SQLiteDataManager

app = Flask(__name__)

data_manager = SQLiteDataManager("moviweb.db")


@app.route('/')
def home():
    """
    Home page route.

    Returns:
        str: A welcome message for the MovieWeb App.
    """
    return "Welcome to MovieWeb App!"


@app.route('/users', methods=['GET'])
def list_users():
    """
    Get a list of all users in the database.

    Returns:
        JSON: A list of all users.
    """
    users = data_manager.get_all_users()
    users_list = [{"id": user.id, "name": user.name} for user in
                  users]
    return jsonify(users_list)


@app.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    """
    Get all movies for a specific user.

    Args:
        user_id (int): The ID of the user whose movies are to be retrieved.

    Returns:
        JSON: A list of all movies for the specified user.
    """
    session = data_manager.Session()
    user = session.query(User).options(
        joinedload(User.movies)).filter(User.id == user_id).first()
    session.close()

    if user:
        movies_list = [
            {
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "year": movie.year,
                "rating": movie.rating
            }
            for movie in user.movies
        ]
        return jsonify(movies_list)

    return jsonify({"error": "User not found"}), 404


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_form(user_id):
    """
    Route to add a new movie to a user's list through a form.

    Args:
        user_id (int): The ID of the user to whom the movie will be added.

    Returns:
        HTML page or JSON response depending on the method.
    """
    if request.method == 'POST':
        title = request.form.get("title")
        director = request.form.get("director")
        year = request.form.get("year")
        rating = request.form.get("rating")

        if not all([title, director, year]):
            return jsonify({
                               "error": "Title, director, and year are required"}), 400

        data_manager.add_movie(user_id, title, director, year,
                               rating)
        return redirect(url_for('user_movies', user_id=user_id))

    return '''
        <form method="POST">
            Title: <input type="text" name="title"><br>
            Director: <input type="text" name="director"><br>
            Year: <input type="text" name="year"><br>
            Rating: <input type="text" name="rating"><br>
            <input type="submit" value="Add Movie">
        </form>
    '''


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>',
           methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Update details of a specific movie in a user's list.

    Args:
        user_id (int): The ID of the user whose movie is to be updated.
        movie_id (int): The ID of the movie to be updated.

    Returns:
        HTML page or JSON response depending on the method.
    """
    if request.method == 'POST':
        title = request.form.get("title")
        director = request.form.get("director")
        year = request.form.get("year")
        rating = request.form.get("rating")

        data_manager.update_movie(movie_id, title=title,
                                  director=director, year=year,
                                  rating=rating)
        return redirect(url_for('user_movies', user_id=user_id))

    return '''
        <form method="POST">
            Title: <input type="text" name="title"><br>
            Director: <input type="text" name="director"><br>
            Year: <input type="text" name="year"><br>
            Rating: <input type="text" name="rating"><br>
            <input type="submit" value="Update Movie">
        </form>
    '''


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>',
           methods=['DELETE'])
def delete_movie(user_id, movie_id):
    """
    Delete a specific movie from a user's list.

    Args:
        user_id (int): The ID of the user whose movie is to be deleted.
        movie_id (int): The ID of the movie to be deleted.

    Returns:
        JSON: A message indicating success or failure.
    """
    data_manager.delete_movie(movie_id)
    return jsonify({
                       "message": f"Movie ID {movie_id} deleted successfully from user ID {user_id}"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
