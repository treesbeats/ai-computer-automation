"""Browser automation with Selenium."""

import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """Web browser automation using Selenium."""

    def __init__(
        self,
        browser: str = "chrome",
        headless: bool = False,
        implicit_wait: int = 10,
    ):
        """
        Initialize browser automation.

        Args:
            browser: Browser to use ('chrome', 'firefox', 'edge')
            headless: Run in headless mode
            implicit_wait: Implicit wait time in seconds
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            self.webdriver = webdriver
            self.By = By
            self.WebDriverWait = WebDriverWait
            self.EC = EC
        except ImportError:
            raise ImportError(
                "Selenium not installed. Install with: pip install selenium"
            )

        self.browser_name = browser.lower()
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.driver = None

        logger.info(
            f"Initialized browser automation (browser={browser}, headless={headless})"
        )

    def start(self) -> None:
        """Start the browser."""
        if self.driver:
            logger.warning("Browser already started")
            return

        if self.browser_name == "chrome":
            options = self.webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = self.webdriver.Chrome(options=options)
        elif self.browser_name == "firefox":
            options = self.webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = self.webdriver.Firefox(options=options)
        elif self.browser_name == "edge":
            options = self.webdriver.EdgeOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = self.webdriver.Edge(options=options)
        else:
            raise ValueError(f"Unsupported browser: {self.browser_name}")

        self.driver.implicitly_wait(self.implicit_wait)
        logger.info(f"Started {self.browser_name} browser")

    def stop(self) -> None:
        """Stop the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Stopped browser")

    def navigate_to(self, url: str) -> None:
        """
        Navigate to URL.

        Args:
            url: URL to navigate to
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        self.driver.get(url)
        logger.debug(f"Navigated to {url}")

    def find_element(self, by: str, value: str, timeout: int = 10):
        """
        Find an element on the page.

        Args:
            by: Locator strategy (e.g., 'id', 'css', 'xpath')
            value: Locator value
            timeout: Maximum wait time

        Returns:
            WebElement
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        by_map = {
            "id": self.By.ID,
            "name": self.By.NAME,
            "class": self.By.CLASS_NAME,
            "tag": self.By.TAG_NAME,
            "css": self.By.CSS_SELECTOR,
            "xpath": self.By.XPATH,
            "link_text": self.By.LINK_TEXT,
            "partial_link_text": self.By.PARTIAL_LINK_TEXT,
        }

        locator = by_map.get(by.lower(), self.By.CSS_SELECTOR)
        element = self.WebDriverWait(self.driver, timeout).until(
            self.EC.presence_of_element_located((locator, value))
        )

        logger.debug(f"Found element: {by}={value}")
        return element

    def find_elements(self, by: str, value: str) -> List:
        """
        Find multiple elements.

        Args:
            by: Locator strategy
            value: Locator value

        Returns:
            List of WebElements
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        by_map = {
            "id": self.By.ID,
            "name": self.By.NAME,
            "class": self.By.CLASS_NAME,
            "tag": self.By.TAG_NAME,
            "css": self.By.CSS_SELECTOR,
            "xpath": self.By.XPATH,
        }

        locator = by_map.get(by.lower(), self.By.CSS_SELECTOR)
        elements = self.driver.find_elements(locator, value)

        logger.debug(f"Found {len(elements)} elements: {by}={value}")
        return elements

    def click(self, by: str, value: str) -> None:
        """
        Click an element.

        Args:
            by: Locator strategy
            value: Locator value
        """
        element = self.find_element(by, value)
        element.click()
        logger.debug(f"Clicked element: {by}={value}")

    def type_text(self, by: str, value: str, text: str) -> None:
        """
        Type text into an element.

        Args:
            by: Locator strategy
            value: Locator value
            text: Text to type
        """
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)
        logger.debug(f"Typed text into element: {by}={value}")

    def get_text(self, by: str, value: str) -> str:
        """
        Get text from an element.

        Args:
            by: Locator strategy
            value: Locator value

        Returns:
            Element text
        """
        element = self.find_element(by, value)
        text = element.text
        logger.debug(f"Got text from element: {by}={value}")
        return text

    def get_attribute(self, by: str, value: str, attribute: str) -> str:
        """
        Get attribute from an element.

        Args:
            by: Locator strategy
            value: Locator value
            attribute: Attribute name

        Returns:
            Attribute value
        """
        element = self.find_element(by, value)
        attr_value = element.get_attribute(attribute)
        logger.debug(f"Got attribute '{attribute}' from element: {by}={value}")
        return attr_value

    def screenshot(self, filepath: str) -> None:
        """
        Take a screenshot.

        Args:
            filepath: Path to save screenshot
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        self.driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved to {filepath}")

    def execute_script(self, script: str, *args):
        """
        Execute JavaScript.

        Args:
            script: JavaScript code
            *args: Arguments to pass to script

        Returns:
            Script return value
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        result = self.driver.execute_script(script, *args)
        logger.debug("Executed JavaScript")
        return result

    def get_current_url(self) -> str:
        """
        Get current URL.

        Returns:
            Current URL
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        return self.driver.current_url

    def get_title(self) -> str:
        """
        Get page title.

        Returns:
            Page title
        """
        if not self.driver:
            raise RuntimeError("Browser not started")

        return self.driver.title

    def wait_for_element(self, by: str, value: str, timeout: int = 10) -> bool:
        """
        Wait for element to appear.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Maximum wait time

        Returns:
            True if element appeared
        """
        try:
            self.find_element(by, value, timeout)
            return True
        except:
            return False

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
