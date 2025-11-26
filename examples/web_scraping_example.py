"""
Web Scraping Example

Demonstrates web automation and scraping using the browser automation module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation.web import BrowserAutomation
from ai_automation.utils import setup_logger
import time


def example_basic_navigation():
    """Basic web navigation example."""
    print("=" * 70)
    print("Basic Web Navigation Example")
    print("=" * 70)
    print()

    try:
        with BrowserAutomation(browser="chrome", headless=True) as browser:
            print("✓ Browser started")

            # Navigate to a website
            print("\nNavigating to example.com...")
            browser.navigate_to("https://example.com")
            print(f"✓ Current URL: {browser.get_current_url()}")
            print(f"✓ Page title: {browser.get_title()}")

            # Take a screenshot
            screenshot_path = "screenshots/example_page.png"
            browser.screenshot(screenshot_path)
            print(f"✓ Screenshot saved to {screenshot_path}")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: This example requires Selenium and a browser driver.")
        print("Install with: pip install selenium")
        print("And install ChromeDriver: https://chromedriver.chromium.org/")


def example_form_interaction():
    """Example of interacting with web forms."""
    print("\n" + "=" * 70)
    print("Form Interaction Example")
    print("=" * 70)
    print()

    try:
        with BrowserAutomation(browser="chrome", headless=True) as browser:
            print("✓ Browser started")

            # Navigate to a form example
            print("\nNavigating to form page...")
            browser.navigate_to("https://httpbin.org/forms/post")
            print(f"✓ Loaded: {browser.get_title()}")

            # Fill form fields (example - adjust selectors as needed)
            print("\nInteracting with form...")

            # Wait a bit for page to load
            time.sleep(1)

            # Get page source to verify
            print("✓ Page loaded successfully")

            # Take screenshot
            screenshot_path = "screenshots/form_page.png"
            browser.screenshot(screenshot_path)
            print(f"✓ Screenshot saved to {screenshot_path}")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: Make sure Selenium and browser drivers are installed.")


def example_data_extraction():
    """Example of extracting data from a web page."""
    print("\n" + "=" * 70)
    print("Data Extraction Example")
    print("=" * 70)
    print()

    try:
        with BrowserAutomation(browser="chrome", headless=True) as browser:
            print("✓ Browser started")

            # Navigate to a page with data
            print("\nNavigating to quotes page...")
            browser.navigate_to("http://quotes.toscrape.com/")
            print(f"✓ Loaded: {browser.get_title()}")

            time.sleep(1)

            # Extract quotes (example)
            print("\nExtracting quotes...")
            try:
                quotes = browser.find_elements("class", "quote")
                print(f"✓ Found {len(quotes)} quotes on the page")

                # Extract first few quotes
                for i, quote in enumerate(quotes[:3], 1):
                    text_elem = quote.find_element("css selector", ".text")
                    author_elem = quote.find_element("css selector", ".author")

                    print(f"\nQuote {i}:")
                    print(f"  Text: {text_elem.text}")
                    print(f"  Author: {author_elem.text}")

            except Exception as e:
                print(f"Note: Could not extract quotes: {e}")

            # Take screenshot
            screenshot_path = "screenshots/quotes_page.png"
            browser.screenshot(screenshot_path)
            print(f"\n✓ Screenshot saved to {screenshot_path}")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: Make sure you have internet connection and Selenium installed.")


def main():
    """Run web scraping examples."""
    # Setup logging
    setup_logger("web_scraping", level="INFO")

    print("\nWeb Scraping and Automation Examples")
    print("=" * 70)
    print("\nNote: These examples require:")
    print("  - Selenium: pip install selenium")
    print("  - ChromeDriver: https://chromedriver.chromium.org/")
    print("  - Internet connection")
    print()

    input("Press Enter to continue...")

    # Run examples
    example_basic_navigation()
    example_form_interaction()
    example_data_extraction()

    print("\n" + "=" * 70)
    print("All web scraping examples completed!")
    print("=" * 70)
    print("\nCheck the 'screenshots' directory for captured screenshots.")


if __name__ == "__main__":
    main()
