from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """
    Abstract base class for managing data operations.
    """

    @abstractmethod
    def get_all_users(self):
        """
        Retrieve all users.

        Returns:
            list: A list of user objects.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
        Retrieve all movies for a specific user.

        Args:
            user_id (int): ID of the user.

        Returns:
            list: A list of movie objects.
        """
        pass

    @abstractmethod
    def add_movie(self, user_id, title, director, year, rating):
        """
        Add a new movie for a specific user.

        Args:
            user_id (int): ID of the user.
            title (str): Movie title.
            director (str): Movie director.
            year (int): Year of the movie.
            rating (float): Rating of the movie.

        Returns:
            None
        """
        pass

    @abstractmethod
    def update_movie(self, movie_id, title=None, director=None,
                     year=None, rating=None):
        """
        Update an existing movie.

        Args:
            movie_id (int): ID of the movie to be updated.
            title (str, optional): Updated title.
            director (str, optional): Updated director.
            year (int, optional): Updated year.
            rating (float, optional): Updated rating.

        Returns:
            None
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """
        Delete a movie.

        Args:
            movie_id (int): ID of the movie to be deleted.

        Returns:
            None
        """
        pass
