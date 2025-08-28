# scraper_app/tasks.py
import os
import time
import json
import logging
import re
from math import ceil
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.db import transaction
from celery import shared_task
from celery.utils.log import get_task_logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager

from .models import Publication, Author
from core.utils import build_tfidf_and_index  # Import TF-IDF rebuild utility

logger = get_task_logger(__name__)

BASE_URL = (
    "https://pureportal.coventry.ac.uk/en/organisations/fbl-school-of-economics-finance-and-accounting/publications/"
)

FIRST_DIGIT = re.compile(r"\d")
NAME_PAIR = re.compile(
    r"[A-Z][A-Za-z'’\-]+,\s*(?:[A-Z](?:\.)?)(?:\s*[A-Z](?:\.)?)*",
    flags=re.UNICODE
)

# ---------------------- Selenium Helpers ----------------------

def build_firefox_options(headless: bool) -> FirefoxOptions:
    opts = FirefoxOptions()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--window-size=1366,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-popup-blocking")
    opts.set_preference("dom.webnotifications.enabled", False)
    opts.set_preference("general.useragent.override",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0")
    return opts

def make_driver(headless: bool = True) -> webdriver.Firefox:
    """Create a Firefox WebDriver suitable for Celery / headless environments."""
    try:
        service = FirefoxService(
            executable_path=GeckoDriverManager().install(),
            log_output=open(os.devnull, 'w')  # suppress geckodriver logs
        )

        driver = webdriver.Firefox(service=service, options=build_firefox_options(headless=True))
        driver.set_page_load_timeout(60)

        # Hide webdriver detection
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except Exception as e:
            logger.warning(f"Failed to hide webdriver: {e}")

        return driver

    except Exception as e:
        logger.error(f"Failed to start Firefox WebDriver: {e}", exc_info=True)
        raise

def accept_cookies_if_present(driver: webdriver.Firefox):
    try:
        btn = WebDriverWait(driver, 6).until(
            lambda d: d.find_element(By.ID, "onetrust-accept-btn-handler")
        )
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.25)
    except Exception:
        pass

# ---------------------- Listing Pages ----------------------

def scrape_listing_page(driver: webdriver.Firefox, page_idx: int) -> List[Dict]:
    url = f"{BASE_URL}?page={page_idx}"
    logger.info(f"Scraping listing page {page_idx + 1}: {url}")
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".result-container h3.title a")
                      or "No results" in d.page_source
        )
    except TimeoutException:
        logger.warning(f"Timeout on page {page_idx + 1}")
        return []

    cards = driver.find_elements(By.CLASS_NAME, "result-container")
    rows: List[Dict] = []
    for c in cards:
        try:
            a = c.find_element(By.CSS_SELECTOR, "h3.title a")
            title = a.text.strip()
            link = a.get_attribute("href")
            if title and link:
                rows.append({"title": title, "link": link})
        except Exception as e:
            logger.debug(f"Failed to parse card on page {page_idx + 1}: {e}")
            continue
    logger.info(f"Found {len(rows)} publications on page {page_idx + 1}")
    return rows

def gather_all_listing_links(max_pages: int, headless_listing: bool = False) -> List[Dict]:
    driver = make_driver(headless_listing)
    try:
        driver.get(BASE_URL)
        accept_cookies_if_present(driver)
        all_rows: List[Dict] = []
        for i in range(max_pages):
            logger.info(f"Processing listing page {i + 1}/{max_pages}")
            rows = scrape_listing_page(driver, i)
            if not rows:
                logger.info(f"Empty at page {i + 1}; stopping early.")
                break
            all_rows.extend(rows)
        # Dedupe by link
        uniq = {r["link"]: r for r in all_rows}
        logger.info(f"Collected {len(uniq)} unique publication links")
        return list(uniq.values())
    finally:
        driver.quit()

# ---------------------- Detail Pages ----------------------

def _uniq(seq: List[Dict]) -> List[Dict]:
    seen, out = set(), []
    for x in seq:
        key = (x['name'].strip(), x.get('profile_url') or '')
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out

def extract_detail_for_link(driver: webdriver.Firefox, link: str, title_hint: str, delay: float) -> Dict:
    driver.get(link)
    accept_cookies_if_present(driver)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
    except TimeoutException:
        logger.warning(f"Timeout loading detail page: {link}")

    # TITLE
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except NoSuchElementException:
        title = title_hint or ""

    # AUTHORS (simple fallback)
    authors = []
    for a in driver.find_elements(By.CSS_SELECTOR, ".relations.persons a[href*='/en/persons/']"):
        try:
            name = a.text.strip()
            url = a.get_attribute("href")
            if name:
                authors.append({"name": name, "profile_url": url})
        except Exception:
            continue
    authors = _uniq(authors)

    # PUBLISHED DATE
    published_date = None
    for sel in ["span.date", "time[datetime]", "time"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            published_date = el.get_attribute("datetime") or el.text.strip()
            if published_date:
                break
        except NoSuchElementException:
            continue

    # ABSTRACT
    abstract_txt = None
    for sel in ["section#abstract .textblock", "section.abstract .textblock", "div.abstract .textblock"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            txt = el.text.strip()
            if txt and len(txt) > 15:
                abstract_txt = txt
                break
        except NoSuchElementException:
            continue

    time.sleep(delay)
    return {
        "title": title,
        "link": link,
        "authors": authors,
        "published_date": published_date,
        "abstract": abstract_txt or ""
    }

def worker_detail_batch(batch: List[Dict], headless: bool, delay: float) -> List[Dict]:
    driver = make_driver(headless)
    results: List[Dict] = []
    try:
        for i, item in enumerate(batch, 1):
            try:
                rec = extract_detail_for_link(driver, item["link"], item.get("title", ""), delay)
                results.append(rec)
                logger.info(f"[WORKER] {i}/{len(batch)} OK: {rec['title'][:60]}")
            except WebDriverException as e:
                logger.error(f"[WORKER] Error scraping {item['link']}: {e}")
    finally:
        driver.quit()
    return results

def chunk(items: List[Dict], n: int) -> List[List[Dict]]:
    if n <= 1:
        return [items]
    size = ceil(len(items) / n)
    return [items[i:i + size] for i in range(0, len(items), size)]

# ---------------------- Celery Task ----------------------

@shared_task(bind=True)
def run_full_scrape(self, max_pages: int = 50, workers: int = 8, delay: float = 0.35, headless_listing: bool = False):
    logger.info(f"Starting scrape task: max_pages={max_pages}, workers={workers}, delay={delay}")
    start_time = time.time()

    # Stage 1: Listing
    listing = gather_all_listing_links(max_pages, headless_listing)
    if not listing:
        logger.warning("No publications found during listing phase")
        return {'status': 'No publications found', 'elapsed_time': time.time() - start_time}

    # Stage 2: Detail scraping in parallel
    batches = chunk(listing, workers)
    all_results: List[Dict] = []

    # ThreadPoolExecutor for non-blocking scraping
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker_detail_batch, batch, True, delay) for batch in batches]
        for fut in as_completed(futures):
            all_results.extend(fut.result() or [])
            logger.info(f"Batch completed, total results so far: {len(all_results)}")

    # Stage 3: Save to DB
    failed_urls = []
    with transaction.atomic():
        for rec in all_results:
            try:
                pub, created = Publication.objects.get_or_create(
                    link=rec['link'],
                    defaults={
                        'title': rec['title'],
                        'published_date': rec['published_date'],
                        'abstract': rec['abstract']
                    }
                )
                if not created:
                    pub.title = rec['title']
                    pub.published_date = rec['published_date']
                    pub.abstract = rec['abstract']
                    pub.save()

                pub.authors.clear()
                for auth in rec['authors']:
                    author, _ = Author.objects.get_or_create(
                        name=auth['name'],
                        defaults={'profile_url': auth.get('profile_url')}
                    )
                    if auth.get('profile_url') and author.profile_url != auth['profile_url']:
                        author.profile_url = auth['profile_url']
                        author.save()
                    pub.authors.add(author)
            except Exception as e:
                logger.error(f"Failed to save publication {rec['link']}: {e}")
                failed_urls.append(rec['link'])

    # Stage 4: Rebuild TF-IDF cache
    try:
        logger.info("Rebuilding TF-IDF cache after scraping...")
        build_tfidf_and_index()
        logger.info("TF-IDF cache rebuilt successfully")
    except Exception as e:
        logger.error(f"Failed to rebuild TF-IDF cache: {e}")

    elapsed_time = time.time() - start_time
    logger.info(f"Scrape task completed in {elapsed_time:.2f}s, {len(all_results)} publications processed, {len(failed_urls)} failed")
    return {
        'status': 'Completed',
        'count': len(all_results),
        'failed_urls': failed_urls,
        'elapsed_time': elapsed_time
    }
