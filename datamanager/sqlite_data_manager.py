from sqlalchemy import create_engine, Column, Integer, String, Float, \
    ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, \
    relationship, declarative_base
from datamanager import DataManagerInterface

Base = declarative_base()


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier for the user.
        name (str): The name of the user.
        movies (list): A list of Movie objects associated with the user.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    movies = relationship("Movie", back_populates="user")


class Movie(Base):
    """
    Represents a movie in the database.

    Attributes:
        id (int): The unique identifier for the movie.
        name (str): The name of the movie.
        director (str): The director of the movie.
        year (int): The year the movie was released.
        rating (float): The rating of the movie.
        user_id (int): The ID of the user who added the movie.
    """
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    director = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="movies")


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        """
        Initialize the SQLiteDataManager with a database file.

        Args:
            db_file_name (str): The name of the SQLite database file.
        """
        self.engine = create_engine(f'sqlite:///{db_file_name}')
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def get_all_users(self):
        """
        Retrieve all users from the database.

        Returns: list: A list of User objects representing all
        users in the database.
        """
        try:
            session = self.Session()
            users = session.query(User).all()
            session.close()
            return users
        except SQLAlchemyError as e:
            print(f"Error getting all users: {e}")
            return []

    def get_user_movies(self, user_id):
        """
        Retrieve all movies for a specific user.

        Args: user_id (int): The ID of the user whose movies are
        to be retrieved.

        Returns:
            list: A list of Movie objects representing the user's
            movies.
        """
        try:
            session = self.Session()
            user = session.query(User).filter(
                User.id == user_id).first()
            session.close()
            if user:
                return user.movies
            return []
        except SQLAlchemyError as e:
            print(f"Error getting user movies: {e}")
            return []

    def add_user(self, user_name):
        """
        Add a new user to the database.

        Args:
            user_name (str): The name of the user to be added.
        """
        try:
            session = self.Session()
            new_user = User(name=user_name)
            session.add(new_user)
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            print(f"Error adding user: {e}")
            session.rollback()

    def add_movie(self, user_id, title, director, year, rating):
        """
        Add a new movie to the database for a specific user.

        Args:
            user_id (int): The ID of the user to whom the movie belongs.
            title (str): The title of the movie.
            director (str): The director of the movie.
            year (int): The year the movie was released.
            rating (float): The rating of the movie.
        """
        try:
            session = self.Session()
            new_movie = Movie(name=title, director=director,
                              year=year, rating=rating,
                              user_id=user_id)
            session.add(new_movie)
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            print(f"Error adding movie: {e}")
            session.rollback()

    def update_movie(self, movie_id, title=None, director=None,
                     year=None, rating=None):
        """
        Update the details of a specific movie in the database.

        Args:
            movie_id (int): The ID of the movie to be updated.
            title (str, optional): The new title of the movie.
            director (str, optional): The new director of the movie.
            year (int, optional): The new year of release of the movie.
            rating (float, optional): The new rating of the movie.
        """
        try:
            session = self.Session()
            movie = session.query(Movie).filter(
                Movie.id == movie_id).first()
            if movie:
                if title:
                    movie.name = title
                if director:
                    movie.director = director
                if year:
                    movie.year = year
                if rating:
                    movie.rating = rating
                session.commit()
            session.close()
        except SQLAlchemyError as e:
            print(f"Error updating movie: {e}")
            session.rollback()

    def delete_movie(self, movie_id):
        """
        Delete a specific movie from the database.

        Args:
            movie_id (int): The ID of the movie to be deleted.
        """
        try:
            session = self.Session()
            movie = session.query(Movie).filter(
                Movie.id == movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
            session.close()
        except SQLAlchemyError as e:
            print(f"Error deleting movie: {e}")
            session.rollback()
