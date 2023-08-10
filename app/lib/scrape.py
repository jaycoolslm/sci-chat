import requests
import time
import os
from bs4 import BeautifulSoup


class ScienceDirect:
    url = "https://api.elsevier.com/content"
    show = 100

    def __init__(self, api_key=None, sleep=0.35, corpus_dir="./corpus"):
        if api_key is None:
            raise ValueError("API key must be provided")
        self.api_key = api_key
        self.sleep = sleep
        self.corpus_dir = corpus_dir

    def scrape_query_results(self, query, override_max_offset=None):
        max_offset = self._request_with_retries(self._get_max_offset, query)
        if override_max_offset is not None:
            max_offset = override_max_offset
        offset = 0
        self.piis = []
        while offset <= max_offset:
            [piis_res, papers] = self._request_with_retries(self._search_request, query, offset)
            self.piis.extend(piis_res)
            offset += self.show
        return papers, len(self.piis)

    def scrape_articles(self):
        if not len(self.piis):
            raise ValueError("No articles to scrape. Please run scrape_query_results first.")
        for pii in self.piis:
            if os.path.isdir(f"{self.corpus_dir}/{pii}"):
                print(f"PII: {pii} already saved.")
                continue
            [abstract, body] = self._request_with_retries(self._article_request, pii)
            if not abstract and not body:
                continue
            os.makedirs(f"{self.corpus_dir}/{pii}", exist_ok=False)
            self._save_text(pii, abstract, body)

    def scrape(self, query, override_max_offset=None):
        max_offset = self._request_with_retries(self._get_max_offset, query)
        if override_max_offset is not None:
            max_offset = override_max_offset
        offset = 0
        piis = []
        while offset <= max_offset:
            piis_res = self._request_with_retries(self._search_request, query, offset)[0] # only return piis
            piis.extend(piis_res)
            offset += self.show
        print("Amount of articles scraped: ", len(piis))
        for pii in piis:
            if os.path.isdir(f"{self.corpus_dir}/{pii}"):
                print(f"PII: {pii} already saved.")
                continue
            [abstract, body] = self._request_with_retries(self._article_request, pii)
            if not abstract and not body:
                continue
            os.makedirs(f"{self.corpus_dir}/{pii}", exist_ok=False)
            self._save_text(pii, abstract, body)

        return piis

    # save parsed text to specified directory
    def _save_text(self, pii, abstract, body):
        abstract_file = open(f"{self.corpus_dir}/{pii}/abstract.txt", "w")
        abstract_file.write(abstract)
        body_file = open(f"{self.corpus_dir}/{pii}/body.txt", "w")
        body_file.write(body)

    # search and return abstract and body of given pii
    def _article_request(self, pii):
        url = f"{self.url}/article/pii/{pii}?httpAccept=text/xml"
        res = requests.get(
            url=url,
            headers={"X-ELS-APIKey": self.api_key},
        )
        if not res.ok:
            return res.status_code, None
        soup = BeautifulSoup(res.text, "lxml")

        body = soup.find("ce:sections") or soup.find("xocs:rawtext")
        if not body:
            print("Your institute does not have access to PII: ", pii)
            return 200, [None, None]
        body = body.get_text()

        abstract = soup.find("dc:description") or soup.find("ce:abstract")
        if abstract:
            abstract = abstract.get_text()
        else:
            abstract = "N/A"

        return res.status_code, [abstract, body]

    # search science direct for articles of given key words
    def _search_request(self, query, offset):
        res = requests.put(
            url=f"{self.url}/search/sciencedirect",
            headers={
                "X-ELS-APIKey": self.api_key,
            },
            json={
                "qs": query,
                "display": {"show": 100, "offset": offset},
            },
        )
        if not res.ok:
            return res.status_code, None
        data = res.json()
        papers = data["results"]
        piis = []
        for paper in papers:
            piis.append(paper["pii"])
        return res.status_code, [piis, papers]

    # handle amount of iterations needed to pull data
    # 6000 is the max offset value possible
    def _get_max_offset(self, query):
        res = requests.put(
            url=f"{self.url}/search/sciencedirect",
            headers={"X-ELS-APIKey": self.api_key},
            json={"qs": query},
        )
        data = res.json()
        if not res.ok:
            return res.status_code, None
        num_of_results = data["resultsFound"]
        return res.status_code, min(num_of_results // self.show * self.show, 6000)

    def _request_with_retries(self, method, *args):
        status_code, result = method(*args)
        while status_code != 200:
            time.sleep(self.sleep)
            status_code, result = method(*args)
        return result
