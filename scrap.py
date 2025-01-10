import time
import re

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ChromeDriver Manager for automatic driver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Googletrans for translation
from googletrans import Translator


def separate_trend_and_volume(trend_text):
    """
    Splits a trailing numeric volume (e.g. '1.4M', '19k', '299 K', '1.1m')
    from the main trend text.

    Returns (trend, volume).

    Examples:
      "Fernanda Torres1.1m"   -> ("Fernanda Torres", "1.1m")
      "#PartGlove1.4M"        -> ("#PartGlove", "1.4M")
      "Liverpool255K"         -> ("Liverpool", "255K")
      "Trudeau"               -> ("Trudeau", "")
    """
    pattern = r'([0-9,.\s]+[kKmM]?)$'
    match = re.search(pattern, trend_text)
    if match:
        volume = match.group(1).strip()
        text = trend_text[:match.start()].strip()
        return text, volume
    else:
        return trend_text, ""


def scrape_trends_with_modal(url="https://trends24.in/", top_n=12, translate=True):
    """
    1) Launches Chrome via Selenium, goes to `url`.
    2) Collects the first `top_n` trend links.
    3) For each trend link:
       - Extracts raw text (e.g. "Trudeau255K").
       - Splits out trailing volume if present.
       - Clicks link to open the modal (#trendcheck-dialog).
       - Scrapes "Trending for" (tc-stat-label == "Trending for").
       - Scrapes "Total Tweets" (tc-stat-label == "Total Tweets") as `volume`.
       - Optionally translates the main trend text to English (translate=True).
    4) Returns a list of dicts: [{"trend_text","volume","trending_for"}].
    """

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Create a single Translator to reuse
    translator = Translator()

    try:
        driver.get(url)
        time.sleep(3)  # give the page time to load

        # If there's a sticky "view-all-button" blocking clicks, remove it
        try:
            view_all_div = driver.find_element(
                By.CSS_SELECTOR,
                "div.view-all-button.left-0.flex.justify-center.w-full.sticky.bottom-2"
            )
            driver.execute_script("arguments[0].remove();", view_all_div)
            time.sleep(1)
        except:
            pass

        # Find the trend links
        trend_links = driver.find_elements(By.CSS_SELECTOR, "ol.trend-card__list li a")

        results = []
        for link in trend_links[:top_n]:
            raw_text = link.text.strip()
            main_trend, volume = separate_trend_and_volume(raw_text)

            # SCROLL & CLICK
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)

            try:
                link.click()
            except:
                # fallback to JS click
                driver.execute_script("arguments[0].click();", link)

            # WAIT FOR MODAL
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "#trendcheck-dialog[open]")
                    )
                )
            except:
                trending_for = ""
            else:
                trending_for = ""
                # PARSE THE MODAL
                stat_blocks = driver.find_elements(
                    By.CSS_SELECTOR, "#trendcheck-dialog .tc-stat-block"
                )
                for block in stat_blocks:
                    dt_text = block.find_element(
                        By.CSS_SELECTOR, "dt.tc-stat-label"
                    ).text.strip()
                    dd_text = block.find_element(
                        By.CSS_SELECTOR, "dd.tc-stat-value"
                    ).text.strip()

                    if dt_text == "Trending for":
                        trending_for = dd_text
                    elif dt_text == "Total Tweets":
                        volume = dd_text  # e.g. "255K"

            # CLOSE MODAL
            try:
                close_btn = driver.find_element(
                    By.CSS_SELECTOR, "#trendcheck-dialog .close-modal"
                )
                close_btn.click()
                time.sleep(1)
            except:
                pass

            # TRANSLATE THE TREND TO ENGLISH (if requested)
            if translate and main_trend:
                try:
                    # You might do a small pause to avoid rate limits
                    time.sleep(0.3)
                    translated_trend = translator.translate(main_trend, dest='en')
                    main_trend = translated_trend.text
                except Exception as e:
                    print(f"Translation error for '{main_trend}': {e}")

            # Build the record
            results.append({
                "trend_text": main_trend,
                "volume": volume,
                "trending_for": trending_for
            })

            time.sleep(0.5)  # short delay before next item

    finally:
        driver.quit()

    return results


def print_in_table(trends, title="Trends"):
    """
    Print the data in columns: No. | Trend | Volume | Trending For
    """
    print(f"\n{title}")
    print("-" * 70)
    header_fmt = "{:<4} | {:<25} | {:<10} | {:<15}"
    print(header_fmt.format("No.", "Trend", "Volume", "Trending For"))
    print("-" * 4 + "+" + "-" * 27 + "+" + "-" * 12 + "+" + "-" * 17)

    for i, item in enumerate(trends, start=1):
        t = item["trend_text"]
        v = item["volume"]
        tf = item["trending_for"]
        print(header_fmt.format(i, t, v, tf))


def main():
    # 1) Scrape top 12 global trends, with translation
    print("Scraping the top 12 global trends from https://trends24.in/ ...")
    global_data = scrape_trends_with_modal(
        url="https://trends24.in/",
        top_n=12,
        translate=True  # set to False if you don't want translation
    )
    print_in_table(global_data, title="Top 12 Global Trends (EN)")

    print("\n" + "="*80 + "\n")

    # 2) Scrape top 12 US trends, with translation
    print("Scraping the top 12 US trends from https://trends24.in/united-states/ ...")
    us_data = scrape_trends_with_modal(
        url="https://trends24.in/united-states/",
        top_n=12,
        translate=True
    )
    print_in_table(us_data, title="Top 12 US Trends (EN)")


if __name__ == "__main__":
    main()
