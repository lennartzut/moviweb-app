import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver():
    """
    Provides a Selenium WebDriver instance for testing.
    """
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


def test_home_page(driver):
    """
    Test the MoviWeb App home page.
    """
    driver.get("http://localhost:5000/")
    assert "MoviWeb App" in driver.title
    heading = driver.find_element(By.CLASS_NAME, "display-3")
    assert "MoviWeb App" in heading.text


def test_list_users_page(driver):
    """
    Test the list of users page.
    """
    driver.get("http://localhost:5000/users")
    assert "Users - MoviWeb App" in driver.title
    heading = driver.find_element(By.CLASS_NAME, "display-4")
    assert "List of Users" in heading.text


def test_add_user(driver):
    """
    Test adding a new user.
    """
    driver.get("http://localhost:5000/users")
    add_user_btn = driver.find_element(
        By.CSS_SELECTOR, '[data-target="#addUserModal"]'
    )
    add_user_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "addUserModalLabel"))
    )
    input_name = driver.find_element(By.ID, "userName")
    input_name.send_keys("Jane Doe")

    submit_btn = driver.find_element(
        By.CSS_SELECTOR, '#addUserModal button[type="submit"]'
    )
    submit_btn.click()

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "addUserModal"))
    )
    assert "Jane Doe" in driver.page_source


def test_user_movies_page(driver):
    """
    Test the user's movie collection page.
    """
    driver.get("http://localhost:5000/users")
    user_link = driver.find_element(By.LINK_TEXT, "Jane Doe")
    user_link.click()

    WebDriverWait(driver, 10).until(
        EC.title_contains("Jane Doe - MoviWeb App")
    )
    heading = driver.find_element(By.CLASS_NAME, "text-light")
    assert "Movie Collection of Jane Doe" in heading.text


def test_add_movie(driver):
    """
    Test adding a movie to a user's collection.
    """
    driver.get("http://localhost:5000/users")
    user_link = driver.find_element(By.LINK_TEXT, "Jane Doe")
    user_link.click()

    WebDriverWait(driver, 10).until(
        EC.title_contains("Jane Doe - MoviWeb App")
    )

    add_movie_btn = driver.find_element(
        By.CSS_SELECTOR, '[data-target="#addMovieModal"]'
    )
    add_movie_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "addMovieModalLabel"))
    )

    search_input = driver.find_element(By.ID, "search-title")
    search_input.send_keys("The Godfather")
    search_btn = driver.find_element(
        By.CSS_SELECTOR, '#search-movie-form button[type="submit"]'
    )
    search_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "search-results-container"))
    )

    movie_checkbox = driver.find_element(
        By.CSS_SELECTOR, '#search-results-container input[name="imdb_ids"]'
    )
    movie_checkbox.click()
    add_movies_btn = driver.find_element(
        By.CSS_SELECTOR, '#confirm-add-form button[type="submit"]'
    )
    add_movies_btn.click()

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "addMovieModal"))
    )
    assert "The Godfather" in driver.page_source


def test_update_movie(driver):
    """
    Test updating a movie in a user's collection.
    """
    driver.get("http://localhost:5000/users")
    user_link = driver.find_element(By.LINK_TEXT, "Jane Doe")
    user_link.click()

    WebDriverWait(driver, 10).until(
        EC.title_contains("Jane Doe - MoviWeb App")
    )

    update_btn = driver.find_element(
        By.CSS_SELECTOR, '.movie-card .btn-warning'
    )
    update_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
    )

    movie_id = update_btn.get_attribute("data-target").split('-')[-1]

    movie_title_input = driver.find_element(By.ID, f"title-{movie_id}")
    movie_title_input.clear()
    movie_title_input.send_keys("The Godfather Updated")

    director_input = driver.find_element(By.ID, f"director-{movie_id}")
    director_input.clear()
    director_input.send_keys("Updated Director")

    year_input = driver.find_element(By.ID, f"year-{movie_id}")
    year_input.clear()
    year_input.send_keys("1973")

    rating_input = driver.find_element(By.ID, f"rating-{movie_id}")
    rating_input.clear()
    rating_input.send_keys("9.9")

    submit_btn = driver.find_element(
        By.CSS_SELECTOR, '.modal.show button[type="submit"]'
    )
    submit_btn.click()

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
    )
    assert "The Godfather Updated" in driver.page_source


def test_delete_movie(driver):
    """
    Test deleting a movie from a user's collection.
    """
    driver.get("http://localhost:5000/users")
    user_link = driver.find_element(By.LINK_TEXT, "Jane Doe")
    user_link.click()

    WebDriverWait(driver, 10).until(
        EC.title_contains("Jane Doe - MoviWeb App")
    )

    delete_btn = driver.find_element(
        By.CSS_SELECTOR, '.movie-card .btn-danger'
    )
    delete_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
    )

    confirm_delete_btn = driver.find_element(
        By.CSS_SELECTOR, '.modal.show button[type="submit"]'
    )
    confirm_delete_btn.click()

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
    )

    movie_cards = driver.find_elements(By.CSS_SELECTOR, '.movie-card')
    for card in movie_cards:
        assert "The Godfather Updated" not in card.text


def test_delete_user(driver):
    """
    Test deleting a user after all their movies have been deleted.
    """
    driver.get("http://localhost:5000/users")

    delete_user_btn = driver.find_element(
        By.CSS_SELECTOR, '[data-target="#deleteUserModal-1"]'
    )
    delete_user_btn.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#deleteUserModal-1")
        )
    )

    confirm_delete_user_btn = driver.find_element(
        By.CSS_SELECTOR, '#deleteUserModal-1 button[type="submit"]'
    )
    confirm_delete_user_btn.click()

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "deleteUserModal-1"))
    )

    users_list = driver.find_element(By.CSS_SELECTOR, ".list-group")
    assert "Jane Doe" not in users_list.text
