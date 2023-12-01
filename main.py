import argparse
import os
import sys
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
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
    book_name, book_author = soup.find('h1').text.split('::')
    image_name = soup.find('div', class_='bookimage').find('img')['src']
    image_link = urljoin(response.url, image_name)
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in genres]
    comments = soup.find_all('div', class_='texts')
    book_comments = [comment.find('span').text for comment in comments]

    book_information = {
        'book_name': f'{book_id}. {book_name.strip()}',
        'book_author': book_author.strip(),
        'book_genres': book_genres,
        'book_comments': book_comments,
        'image_link': image_link,
    }

    return book_information


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
        response = requests.get(download_url, params=payload)
        response.raise_for_status()
        book_url = f'{url}b{book_id}/'
        response_book = requests.get(book_url)
        response_book.raise_for_status()

        try:
            check_for_redirect(response.history)
            characteristic_book = parse_book_page(response_book, book_id)
            book_name = characteristic_book['book_name']
            image_link = characteristic_book['image_link']
            download_txt(response.url, book_name)
            download_image(image_link)
            print(f'{book_id}. book downloaded')

        except requests.exceptions.HTTPError:
            print(f'{book_id}. book is missing')
            continue
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            print("Отсутствие соединения, ожидание 5сек...", file=sys.stderr)
            sleep(5)


if __name__ == '__main__':
    main()
