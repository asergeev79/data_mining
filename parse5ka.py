import time
import json
from pathlib import Path
import requests

"""
GET
POST
PUT
PATCH
DELETE
"""

"""
1xx
2xx
3xx
4xx
5xx
"""


# headers = {
#     'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0"
# }
# params = {
#     'records_per_page': 50,
#     'page': 1,
# }
# url = 'https://5ka.ru/api/v2/special_offers/'
# response = requests.get(url, headers=headers)
#
# with open('5ka.html', 'w', encoding='UTF-8') as file:
#     file.write(response.text)

class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parser5ka:
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    params = {
    }

    def __init__(self, category_url, product_url):
        self.category_url = category_url
        self.product_url = product_url

    def _get_response(self, url, **kwargs):
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code != 200:
                    raise StatusCodeError(f'status {response.status_code}')
                return response
            except (requests.exceptions.ConnectTimeout,
                    StatusCodeError):
                time.sleep(0.1)

    def run(self):
        response = self._get_response(self.category_url, headers=self.headers)
        categories: dict = response.json()
        for category in categories:
            self.params['categories'] = category['parent_group_code']
            category['products'] = []
            for products in self.parse(self.product_url):
                category['products'] += products
            file_path = Path(__file__).parent.joinpath(f'{category["parent_group_code"]}.json')
            self.save_file(file_path, category)

    def parse(self, url):
        while url:
            response = self._get_response(url, headers=self.headers, params=self.params)
            data: dict = response.json()
            url = data['next']
            yield data.get('results', [])

    def save_file(self, file_path: Path, data: dict):
        with open(file_path, 'w', encoding='UTF-8') as file:
            # file.write(json.dumps(data))
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka('https://5ka.ru/api/v2/categories/', 'https://5ka.ru/api/v2/special_offers/')
    parser.run()
