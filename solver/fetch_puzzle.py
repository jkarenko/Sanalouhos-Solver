import browser_cookie3
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def fetch_puzzle():
    url = "https://sanalouhos.datadesk.hs.fi"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--disable-notifications')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        return _fetch_puzzle(driver, url)
    finally:
        driver.quit()


def _fetch_puzzle(driver, url):
    try:
        cookies = browser_cookie3.chrome(domain_name='.hs.fi')
    except PermissionError:
        print("Unable to access Chrome cookies. Proceeding without cookies.")
        cookies = []

    driver.get(url)

    for cookie in cookies:
        cookie_dict = {'name': cookie.name, 'value': cookie.value, 'domain': cookie.domain}
        driver.add_cookie(cookie_dict)

    driver.get(url)

    # Wait for either the start button or the game container
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.start-prompt button.button.large.wide.primary.center-content, .game-container"))
        )
    except TimeoutException:
        print("Neither start button nor game container found. Saving screenshot for debugging.")
        driver.save_screenshot("debug_screenshot.png")
        raise

    # Check if start button exists and click it
    try:
        start_button = driver.find_element(By.CSS_SELECTOR,
                                           "div.start-prompt button.button.large.wide.primary.center-content")
        start_button.click()
        print("Start button clicked.")
    except NoSuchElementException:
        print("Start button not found. Assuming game has already started.")

    # Wait for game container
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".game-container"))
        )
        print("Game container found.")
    except TimeoutException:
        print("Game container not found. Saving screenshot for debugging.")
        driver.save_screenshot("debug_screenshot.png")
        raise

    # Wait for buttons to be present
    try:
        buttons = WebDriverWait(driver, 1).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id^='game-tile-']"))
        )
        print(f"Found {len(buttons)} game tiles.")
    except TimeoutException as e:
        print("No buttons found. Saving screenshot for debugging.")
        driver.save_screenshot("debug_screenshot.png")
        raise NoSuchElementException("No game tiles found") from e

    letters = []
    for button in buttons:
        try:
            span = WebDriverWait(button, 1).until(
                EC.presence_of_element_located((By.TAG_NAME, "span"))
            )
            letters.append(span.text.upper())
        except TimeoutException:
            print(f"Span not found in button {button.get_attribute('id')}. Skipping.")

    if not letters:
        print("No letters found. Saving screenshot for debugging.")
        driver.save_screenshot("debug_screenshot.png")
        raise NoSuchElementException("No letters found in game tiles")

    return [letters[i:i + 5] for i in range(0, len(letters), 5)]


def print_grid(grid):
    for row in grid:
        print(''.join(row))


if __name__ == "__main__":
    try:
        puzzle_grid = fetch_puzzle()
        print_grid(puzzle_grid)
    except Exception as e:
        print(f"An error occurred: {e}")
