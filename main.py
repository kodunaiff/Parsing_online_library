import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response_id):
    if response_id:
        raise requests.exceptions.HTTPError


def call_book(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text
    title_text_1 = title_text.split('::')
    return f'{book_id}.{title_text_1[0].strip()}', title_text_1[1].strip()


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    folder_f = sanitize_filename(folder)
    filename_f = sanitize_filename(filename)
    save_path = os.path.join(folder_f, f'{filename_f}.txt')
    with open(save_path, 'wb') as file:
        file.write(response.content)


os.makedirs('books', exist_ok=True)
books_count = 10
library_books = []
for book_id in range(1, books_count + 1):
    url = "https://tululu.org/txt.php"
    payload = {
        'id': f'{book_id}',
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    try:
        mistake_book = check_for_redirect(response.history)
        name_b, author_b = call_book(book_id)
        download_txt(response.url, name_b)
    except requests.exceptions.HTTPError:
        continue

