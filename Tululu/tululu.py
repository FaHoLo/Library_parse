import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


tululu_logger = logging.getLogger('tululu_logger')


# Book info
def fetch_book_webpage(book_url):
    response = requests.get(book_url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 302:
        tululu_logger.debug(f'No book for {book_url}')
        return None
    tululu_logger.debug(f'Book webpage was fetched')
    return BeautifulSoup(response.text, 'lxml')

def get_book_title_and_author(book_webpage):
    title_tag = book_webpage.select_one('h1')
    title = title_tag.text.split('::')
    book_title = title[0].strip()
    book_author = title[1].strip()
    tululu_logger.debug(f'Got book title and author: {book_title} - {book_author}')
    return book_title, book_author

def get_book_comments(book_webpage):
    comment_divs = book_webpage.select('.texts .black')
    comments = [comment.text for comment in comment_divs]
    tululu_logger.debug(f'Got comments to book')
    return comments

def get_book_genres(book_webpage):
    genre_tags = book_webpage.select('span.d_book a')
    genres = [genre.text for genre in genre_tags]
    return genres
# End book info


# Text
def download_book_text(book_id, book_title, dest_folder):
    filename = f'{book_id}. {book_title}'
    filepath = os.path.join(dest_folder, 'books')
    text_url = f'http://tululu.org/txt.php?id={book_id}'
    txt_path = download_txt(text_url, filename, filepath)
    tululu_logger.debug(f'Book with {book_id} was downloaded to path: {txt_path}')
    return txt_path

def download_txt(url, filename, folder='books'):
    text = fetch_text(url)
    if not text:
        return
    filepath = save_txt(text, filename, folder)
    tululu_logger.debug(f'Text was downloaded to {filepath}')
    return filepath

def fetch_text(url):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 301:
        tululu_logger.debug(f'No text for {url}')
        return None
    tululu_logger.debug(f'Text was fetched on url: {url}')
    return response.text

def save_txt(text, filename, folder):
    filename = f'{filename}.txt'
    filepath = collect_filepath(filename, folder)
    with open(filepath, 'w') as file:
        file.write(text)
    tululu_logger.debug(f'Text was saved to {filepath}')
    return filepath

def collect_filepath(filename, folder):
    filename = sanitize_filename(filename)
    folder = folder.rstrip('/\\')
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    tululu_logger.debug(f'Filepath "{filepath}" was collected')
    return filepath
# End text


# Image
def download_book_image(book_url, book_webpage, dest_folder):
    image_url = fetch_image_url(book_webpage, book_url)
    filepath = os.path.join(dest_folder, 'images')
    image_name = image_url.split('/')[-1]
    image_path = download_image(image_url, image_name, filepath)
    tululu_logger.debug(f'Book image to {book_url} was downloaded to path: {image_path}')
    return image_path

def fetch_image_url(book_webpage, book_url):
    image_src = book_webpage.select_one('.bookimage img')['src']
    image_url = urljoin(book_url, image_src)
    tululu_logger.debug(f'Got image url {image_url}')
    return image_url

def download_image(url, filename, folder='images'):
    image = fetch_image(url)
    filepath = collect_filepath(filename, folder)
    if os.path.exists(filepath):
        tululu_logger.debug(f'Image with such name "{filename}" already exists')
        return filepath
    with open(filepath, 'wb') as file:
        file.write(image)
    tululu_logger.debug(f'Image was downloaded to {filepath}')
    return filepath

def fetch_image(url):
    response = requests.get(url)
    response.raise_for_status()
    tululu_logger.debug(f'Text was fetched on url: {url}')
    return response.content
# End image
