import argparse
import logging
import os
import sys
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(response, filename, folder='books/'):
    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    save_path = os.path.join(folder, f'{filename}.txt')
    with open(save_path, 'wb') as file:
        file.write(response.content)


def download_image(image_link, folder='images/'):
    response = requests.get(image_link)
    response.raise_for_status()
    image_part = urlsplit(image_link)
    filename, file_extension = os.path.splitext(image_part.path)
    image_filename = filename.split('/')
    save_path = os.path.join(f'{folder}{image_filename[-1]}{file_extension}')
    with open(save_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(response, book_id):
    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = soup.select_one('h1').text.split('::')
    image_url = soup.select_one('div.bookimage img')['src']
    image_link = urljoin(response.url, image_url)
    genres = soup.select('span.d_book a')
    book_genres = [genre.text for genre in genres]
    comments = soup.select('div.texts span')
    book_comments = [comment.text for comment in comments]

    book = {
        'book_name': f'{book_name.strip()}',
        'book_author': book_author.strip(),
        'book_genres': book_genres,
        'book_comments': book_comments,
        'image_link': image_link,
    }

    return book


def create_books_id():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивания книг'
    )
    parser.add_argument(
        '-s',
        '--start_id',
        help='введите номер с какой книги скачать',
        type=int,
        default=1
    )
    parser.add_argument(
        '-e',
        '--end_id',
        help='введите номер до какой книги скачать',
        type=int,
        default=10
    )
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    return start_id, end_id


def main():
    os.makedirs('books', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    start_id, end_id = create_books_id()

    url = 'https://tululu.org/'
    for book_id in range(start_id, end_id + 1):
        download_url = f'{url}txt.php'
        payload = {
            'id': f'{book_id}',
        }

        try:
            response = requests.get(download_url, params=payload)
            response.raise_for_status()
            check_for_redirect(response)
            book_url = f'{url}b{book_id}/'
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            check_for_redirect(book_response)
            book = parse_book_page(book_response, book_id)
            book_name = book['book_name']
            image_link = book['image_link']
            download_txt(response, book_name)
            download_image(image_link)
            print(f'{book_id}. book downloaded')

        except requests.exceptions.HTTPError:
            logging.warning(f'{book_id}. book is missing'),
            continue
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            print(f"{book_id}. Отсутствие соединения, ожидание 5сек...", file=sys.stderr)
            sleep(5)


if __name__ == '__main__':
    main()
