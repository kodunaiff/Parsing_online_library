import os
from urllib.parse import urljoin
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response_id):
    if response_id:
        raise requests.exceptions.HTTPError


def call_book(link, book_id):
    url = f'{link}b{book_id}/'
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


def download_image(link, book_id, folder='images/'):
    url = f'{link}b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    image_name = soup.find('div', class_='bookimage').find('img')['src']
    image_link = urljoin(url, image_name)
    response_image = requests.get(image_link)
    response_image.raise_for_status()
    image_part = urlsplit(image_link)
    url_parts = image_part.path
    filename, file_extension = os.path.splitext(url_parts)
    image_filename = filename.split('/')
    save_path = os.path.join(f'{folder}{image_filename[-1]}{file_extension}')
    with open(save_path, 'wb') as file:
        file.write(response_image.content)


def download_comments(link, book_id):
    url = f'{link}b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    comments = []
    soup = BeautifulSoup(response.text, 'lxml')
    ing_com = soup.find_all('div', class_='texts')
    for i in ing_com:
        tex = i.find('span').text
        if tex:
            comments.append(tex)
    return comments


os.makedirs('books', exist_ok=True)
os.makedirs('images', exist_ok=True)
os.makedirs('comments', exist_ok=True)
books_count = 10
library_books = []
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
        name_b, author_b = call_book(main_url, book_id)
        #download_txt(response.url, name_b)
        #download_image(main_url, book_id)
        print(download_comments(main_url, book_id))
    except requests.exceptions.HTTPError:
        continue
