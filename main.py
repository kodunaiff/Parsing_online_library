import os
from urllib.parse import urljoin
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response_id):
    if response_id:
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


def parse_book_page(link, book_id):
    url = f'{link}b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = soup.find('h1').text.split('::')
    image_name = soup.find('div', class_='bookimage').find('img')['src']
    image_link = urljoin(url, image_name)
    book_genre = []
    genres = soup.find('span', class_='d_book').find_all('a')
    for genre in genres:
        book_genre.append(genre.text)
    book_comments = []
    comments = soup.find_all('div', class_='texts')
    for comment in comments:
        book_comments.append(comment.find('span').text)

    book_information = {
        'book_name': f'{book_id}. {book_name.strip()}',
        'book_author': book_author.strip(),
        'book_genre': book_genre,
        'book_comments': book_comments,
        'image_link': image_link,
    }

    return book_information


os.makedirs('books', exist_ok=True)
os.makedirs('images', exist_ok=True)

books_count = 10
main_url = "https://tululu.org/"
for book_id in range(1, books_count + 1):
    url = f"{main_url}txt.php"
    payload = {
        'id': f'{book_id}',
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    try:
        mistake_book = check_for_redirect(response.history)
        descript_book = parse_book_page(main_url, book_id)
        book_name = descript_book['book_name']
        image_link = descript_book['image_link']
        download_txt(response.url, book_name)
        download_image(image_link)

    except requests.exceptions.HTTPError:
        continue
