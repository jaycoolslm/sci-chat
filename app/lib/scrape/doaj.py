import os, re, time, json, requests, shutil
import os, re, time, json, requests, shutil
from bs4 import BeautifulSoup

class ScrapeDoaj:
    url = 'https://doaj.org/api/search/articles'
    show = 100

    def __init__(self, corpus_dir="./doaj"):
        self.corpus_dir = corpus_dir
        if not os.path.exists(self.corpus_dir):
            os.makedirs(self.corpus_dir)
        
    def scrape(self, query, filename="a", override_max_offset=None):
        
        max_offset = self._get_max_offset(query)
        offset = 0
        articles = []
        while offset <= max_offset:
            results = self._search_request(query, offset)
            articles.extend(results)
            offset += 1

        print("Amount of articles scraped: ", len(articles))
        # check publisher
        # scrape text if elsevier or mdpi
        # for article in articles:
        #     publisher = article["bibjson"]["journal"]["publisher"]
        #     url = article["bibjson"]["link"][0]["url"]
        #     text = self._fetch_request(url)
        #     soup = BeautifulSoup(text, "html.parser")
        #     sections = soup.find_all('section', id=re.compile('.*sec.*')) or soup.find_all('div', class_="html-p")
        #     if not sections:
        #         print("No sections found in ", url)
        #         continue
        #     section_texts = [section.get_text() for section in sections]
        #     article["body"] = " ".join(section_texts)

            # if publisher == "MDPI AG":
            #     xx
            # elif publisher == "Elsevier":
            #     xx
            # else: pass
        # count = 0
        filtered_articles = [
            record for record in articles
            if all(
                key in record["bibjson"] for key in [
                    "journal", 
                    "year", 
                    "author", 
                    "link", 
                    "title"
                ]
            ) 
            and "title" in record["bibjson"]["journal"] 
            and "publisher" in record["bibjson"]["journal"]
            and record["bibjson"]["link"] 
            and "publisher" in record["bibjson"]["journal"]
            and record["bibjson"]["link"] 
            and "url" in record["bibjson"]["link"][0]
        ]
        try:
            os.remove(f"{self.corpus_dir}/{filename}.json")
            print(f"File {self.corpus_dir}/{filename} has been deleted successfully!")
        except Exception as e:
            print(f"Error deleting file {self.corpus_dir}/{filename}. Reason: {e}")

        try:
            os.remove(f"{self.corpus_dir}/{filename}.json")
            print(f"File {self.corpus_dir}/{filename} has been deleted successfully!")
        except Exception as e:
            print(f"Error deleting file {self.corpus_dir}/{filename}. Reason: {e}")

        with open(os.path.join(self.corpus_dir, f"{filename}.json"), 'w') as json_file:
                json.dump(filtered_articles, json_file, indent=2)

        # delete old vector db so chat will be reinitialized
        try:
            shutil.rmtree("./vectordb/metadata")
        except Exception as e:
            print(f"Error occurred while deleting vector db: {str(e)}")

        # delete old vector db so chat will be reinitialized
        try:
            shutil.rmtree("./vectordb/metadata")
        except Exception as e:
            print(f"Error occurred while deleting vector db: {str(e)}")

        return filtered_articles, len(filtered_articles)

        


    def _get_max_offset(self, query):
        res = requests.get(
            url=f"{self.url}/{query}",
        )
        data = res.json()
        if not res.ok:
            raise ValueError("Unable to fetch articles")
        num_of_results = data["total"]
        print("TOTAL RESULTS", num_of_results)
        return min(num_of_results // self.show, 1000 / self.show)

    def _search_request(self, query, offset):
        res = requests.get(
            url=f"{self.url}/{query}",
            params={
                "pageSize": self.show,
                "page": offset + 1,
            }
        )
        if not res.ok:
            return res.status_code, None
        data = res.json()
        results = data["results"]
        return results
    
    def _fetch_request(self, url):
        try:
            res = requests.get(url)
        except Exception as e:
            print(f"Error occurred while processing Article: {url}")
            print(str(e))
            return ""
        return res.text
    
    def _request_with_retries(self, method, *args):
        status_code, result = method(*args)
        while status_code != 200:
            time.sleep(0.35)
            status_code, result = method(*args)
        return result