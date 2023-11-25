import requests
import os

os.makedirs('books', exist_ok=True)

books_id = [1,2,3,4,5,6,7,8,9,10]

for book_id in books_id:
    url = f"https://tululu.org/txt.php?id={book_id}"
    response = requests.get(url)
    response.raise_for_status()

    filename = f'id{book_id}.txt'
    with open(f'books/{filename}', 'wb') as file:
        file.write(response.content)