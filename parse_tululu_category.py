import argparse
import json
import logging
import os
import sys
from time import sleep
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

from tululu import download_txt, download_image, check_for_redirect, parse_book_page


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивания книг со страниц по категориям'
    )
    parser.add_argument(
        '-s',
        '--start_page',
        help='введите номер, с какой страницы скачать книги',
        type=int,
        default=1
    )
    parser.add_argument(
        '-e',
        '--end_page',
        help='введите номер, до какой страницы скачиваем книги',
        type=int,
        default=2
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_true',
        help='не скачивать картинки'
    )
    parser.add_argument(
        '--skip_txt',
        action='store_true',
        help='не скачивать текст'
    )
    parser.add_argument(
        '--dest_folder',
        type=str,
        help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON',
        default='library_folder/'
    )

    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    dest_folder = args.dest_folder
    return start_page, end_page, skip_imgs, skip_txt, dest_folder


def main():
    start_page, end_page, skip_imgs, skip_txt, library_folder = parse_arguments()
    os.makedirs(f'{library_folder}', exist_ok=True)
    last_page = max(start_page, end_page)
    library = []
    for book_page in range(start_page, last_page + 1):
        url = f'https://tululu.org/l55/{book_page}/'
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books_selector = 'div.bookimage a'
            books = soup.select(books_selector)
            for book in books:
                book_number = book['href']
                book_id = book_number[2:-1]
                book_link = urljoin(url, book_number)
                book_url = urlsplit(url)
                download_url = f'https://{book_url.netloc}/txt.php'

                payload = {
                    'id': f'{book_id}',
                }

                try:
                    book_txt_response = requests.get(download_url, params=payload)
                    book_txt_response.raise_for_status()
                    check_for_redirect(book_txt_response)
                    book_response = requests.get(book_link)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)
                    book_characteristic = parse_book_page(book_response, book_id)
                    book_name = book_characteristic['book_name']
                    image_link = book_characteristic['image_link']
                    library.append(book_characteristic)
                    if not skip_txt:
                        download_txt(book_txt_response, book_name, f'{library_folder}')
                        print(f'{book_id}. book downloaded')
                    if not skip_imgs:
                        download_image(image_link, f'{library_folder}')

                except requests.exceptions.HTTPError:
                    logging.warning(f'{book_id}. book is missing')
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    print(f"{book_id}. Отсутствие соединения, ожидание 5сек...", file=sys.stderr)
                    sleep(5)

        except requests.exceptions.HTTPError:
            logging.warning(f'page № {start_page - 1} is missing')
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            print(f"page № {start_page - 1}. Отсутствие соединения, ожидание 5сек...", file=sys.stderr)
            sleep(5)

    with open(f"{library_folder}/library.json", "w", encoding='utf8') as file:
        json.dump(library, file, ensure_ascii=False)


if __name__ == '__main__':
    main()
