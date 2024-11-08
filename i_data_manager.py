from abc import ABC, abstractmethod


class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def add_movie(self, user_id, title, director, year, rating):
        pass

    @abstractmethod
    def update_movie(self, movie_id, title=None, director=None,
                     year=None, rating=None):
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        pass
