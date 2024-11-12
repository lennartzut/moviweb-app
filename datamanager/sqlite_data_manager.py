from sqlalchemy import create_engine, Column, Integer, String, \
    Float, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, \
    relationship, declarative_base
from datamanager import DataManagerInterface

Base = declarative_base()


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): User's unique ID.
        name (str): User's name.
        movies (list): List of associated Movie objects.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    movies = relationship("Movie", back_populates="user")


class Movie(Base):
    """
    Represents a movie in the database.

    Attributes:
        id (int): Movie's unique ID.
        name (str): Name of the movie.
        director (str): Director of the movie.
        year (int): Year of release.
        rating (float): Rating of the movie.
        user_id (int): ID of user who added the movie.
        imdb_id (str): IMDb ID for movie poster.
    """
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    director = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    imdb_id = Column(String, nullable=False)
    user = relationship("User", back_populates="movies")


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        """
        Initialize SQLiteDataManager.

        Args:
            db_file_name (str): SQLite database file name.
        """
        self.engine = create_engine(f'sqlite:///{db_file_name}')
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def get_all_users(self):
        """
        Retrieve all users from the database.

        Returns:
            list: List of User objects.
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
        Retrieve movies for a specific user.

        Args:
            user_id (int): ID of the user.

        Returns:
            list: List of Movie objects.
        """
        try:
            session = self.Session()
            user = session.query(User).filter(User.id == user_id).first()
            session.close()
            return user.movies if user else []
        except SQLAlchemyError as e:
            print(f"Error getting user movies: {e}")
            return []

    def add_user(self, user_name):
        """
        Add a new user to the database.

        Args:
            user_name (str): Name of the user.
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

    def add_movie(self, user_id, title, director, year, rating,
                  imdb_id):
        """
        Add a movie to the database.

        Args:
            user_id (int): ID of the user.
            title (str): Movie title.
            director (str): Director of the movie.
            year (int): Year of release.
            rating (float): Rating of the movie.
            imdb_id (str): IMDb ID for the movie.
        """
        session = self.Session()
        try:
            formatted_title = title.title()
            new_movie = Movie(
                name=formatted_title, director=director,
                year=year, rating=rating, user_id=user_id,
                imdb_id=imdb_id
            )
            session.add(new_movie)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error adding movie: {e}")
            session.rollback()
        finally:
            session.close()

    def update_movie(self, movie_id, title=None, director=None,
                     year=None, rating=None):
        """
        Update movie details in the database.

        Args:
            movie_id (int): Movie's ID.
            title (str, optional): Updated title.
            director (str, optional): Updated director.
            year (int, optional): Updated year of release.
            rating (float, optional): Updated rating.
        """
        try:
            session = self.Session()
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
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
        Delete a movie from the database.

        Args:
            movie_id (int): ID of the movie to delete.
        """
        try:
            session = self.Session()
            movie = session.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                session.delete(movie)
                session.commit()
            session.close()
        except SQLAlchemyError as e:
            print(f"Error deleting movie: {e}")
            session.rollback()
