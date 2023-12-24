import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
from main import download_txt, download_image, check_for_redirect, parse_book_page
import os
import logging
import sys
from time import sleep
import json

os.makedirs('books', exist_ok=True)
os.makedirs('images', exist_ok=True)

page_number = 1
page_number_off = 4
library = []
while page_number <= page_number_off:
    url = f'https://tululu.org/l55/{page_number}/'

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    page_number += 1
    books_number = soup.find_all('div', class_='bookimage')

    for book_number in books_number:
        book = book_number.find('a')['href']
        book_id = book[2:-1]
        book_link = urljoin(url, book)
        book_url = urlsplit(url)
        download_url = f'https://{book_url.netloc}/txt.php'
        payload = {
            'id': f'{book_id}',
        }
        try:
            response_book = requests.get(download_url, params=payload)
            response_book.raise_for_status()
            check_for_redirect(response_book)
            book_response = requests.get(book_link)
            book_response.raise_for_status()
            check_for_redirect(book_response)
            book_characteristic = parse_book_page(book_response, book_id)
            book_name = book_characteristic['book_name']
            image_link = book_characteristic['image_link']
            download_txt(response_book, book_name)
            download_image(image_link)
            library.append(book_characteristic)
            print(f'{book_id}. book downloaded')
        except requests.exceptions.HTTPError:
            logging.warning(f'{book_id}. book is missing'),
            # continue
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            print(f"{book_id}. Отсутствие соединения, ожидание 5сек...", file=sys.stderr)
            sleep(5)

library_json = json.dumps(library, ensure_ascii=False).encode('utf8')
with open("library.json", "w", encoding='utf8') as my_file:
    my_file.write(library_json.decode())
