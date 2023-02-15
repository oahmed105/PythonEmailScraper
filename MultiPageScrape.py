from bs4 import BeautifulSoup
from selenium import webdriver
import re
import requests
from collections import deque
from urllib.parse import urlsplit
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

query = 'site:linkedin.com "@gmail.com" "ceo"'
links = []

# Enter number of pages to scrape
n_pages = 5
for page in range(1, n_pages):
    url = 'https://www.google.com/search?q=' + query + '&start=' + str((page - 1) * 10)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    time.sleep(10)

    # to save urls to be scraped
    unscraped = deque([url])

    # to save scraped urls
    scraped = set()

    # to save fetched emails
    emails = set()

    while len(unscraped):
        url = unscraped.popleft()
        scraped.add(url)

        parts = urlsplit(url)

        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if '/' in parts.path:
            path = url[:url.rfind('/') + 1]
        else:
            path = url

        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue

        new_emails = set(re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.com", response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')

    for anchor in soup.find_all("a"):
        if "href" in anchor.attrs:
            link = anchor.attrs["href"]
        else:
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''

            if link.startswith('/'):
                link = base_url + link

            elif not link.startswith('http'):
                link = path + link

            if not link.endswith(".gz"):
                if not link in unscraped and not link in scraped:
                    unscraped.append(link)

    df = pd.DataFrame(emails, columns=["Email"])
    df.to_csv('Email_Osama Ahmed.csv', mode='a', index=False)

    print(df)

