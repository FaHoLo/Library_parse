
import os
import json
import tululu
import logging
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


category_logger = logging.getLogger('category_logger')

DEST_FOLDER = ''
SKIP_IMGS = False
SKIP_TXT = False


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # level='DEBUG',
    )
    args = parse_args()
    handle_global_args(args)
    start_page, end_page = handle_page_args(args.start_page, args.end_page)
    json_path = handle_json_arg(args.json_path)
    category_logger.debug('All arguments were parsed and handled')
    category_url = 'http://tululu.org/l55/'
    download_category_books(category_url, start_page, end_page, json_path)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Программа скачает книги с сайта tululu.org'
    )
    parser.add_argument('-s', '--start_page', type=int, help='Номер первой страницы скачивания')
    parser.add_argument('-e', '--end_page', type=int, help='Номер страницы, до которой будут скачаны книги')
    parser.add_argument('-d', '--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгами, json')
    parser.add_argument('-i', '--skip_imgs', action='store_true', help='Не скачивать обложки книг')
    parser.add_argument('-t', '--skip_txt', action='store_true', help='Не скачивать текст книг')
    parser.add_argument('-j', '--json_path', help='Указать свой путь к *.json файлу с результатами')
    return parser.parse_args()

def handle_global_args(args):
    global DEST_FOLDER, SKIP_IMGS, SKIP_TXT
    if args.dest_folder:
        DEST_FOLDER = args.dest_folder
        os.makedirs(DEST_FOLDER, exist_ok=True)
    SKIP_IMGS = args.skip_imgs
    SKIP_TXT = args.skip_txt

def handle_page_args(start_page, end_page):
    if not start_page:
        start_page = 1
    if not end_page:
        end_page = 9999
    return start_page, end_page

def handle_json_arg(json_path):
    if not json_path:
        json_path = ''
    else:
        os.makedirs(json_path, exist_ok=True)
    return json_path

def download_category_books(category_url, start_page, end_page, json_path):
    book_urls = get_category_book_urls(category_url, start_page, end_page)
    book_descriptions = list(filter(None, [download_book(url) for url in book_urls]))
    save_json(book_descriptions, 'book_descriptions', json_path)
    download_book(book_urls[3])
    category_logger.debug('Books were saved')

def get_category_book_urls(category_url, start_page, end_page):
    book_urls = []
    for page in range(start_page, end_page):
        page_url = f'{category_url}/{page}/'
        urls = get_page_book_urls(page_url)
        if not urls:
            break
        book_urls.extend(urls)
    category_logger.debug(f'Got {len(book_urls)} book urls')
    return book_urls
    
def get_page_book_urls(page_url):
    webpage = fetch_category_webpage(page_url)
    if not webpage:
        return
    book_tags = webpage.select('.ow_px_td .d_book')
    book_urls = [urljoin(page_url, book_tag.select_one('a')['href']) for book_tag in book_tags]
    category_logger.debug(f'Got urls form page "{page_url}"')
    return book_urls

def fetch_category_webpage(page_url):
    response = requests.get(page_url, allow_redirects=False)
    if not tululu.is_good_response(response):
        return
    category_logger.debug(f'Category webpage was fetched')
    return BeautifulSoup(response.text, 'lxml')

def download_book(book_url):
    book_path = ''
    image_path = ''
    book_id = book_url.split('/')[-2][1:]
    book_webpage = tululu.fetch_book_webpage(book_url)
    title, author = tululu.get_book_title_and_author(book_webpage)
    if not SKIP_TXT:
        book_path = tululu.download_book_text(book_id, title, DEST_FOLDER)
        if not book_path:
            return
    if not SKIP_IMGS:
        image_path = tululu.download_book_image(book_url, book_webpage, DEST_FOLDER)
    book_description = collect_book_description(book_webpage, book_path, image_path, title, author)
    category_logger.debug(f'Book with id "{book_id}" was downloaded')
    return book_description

def collect_book_description(book_webpage, book_path, image_path, title, author):
    comments = tululu.get_book_comments(book_webpage)
    genres = tululu.get_book_genres(book_webpage)
    book_description = {
        'title': title,
        'author': author,
        'book_path': book_path,
        'image_path': image_path,
        'comments': comments,
        'genres': genres,
    }
    category_logger.debug('Book description collected')
    return book_description

def save_json(info, filename, json_path=''):
    if json_path:
        folder = json_path
    else:
        folder = DEST_FOLDER
    filename = f'{filename}.json'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(info, file, ensure_ascii=False)
    category_logger.debug(f'Json saved to {filename}')
    return filename


if __name__ == '__main__':
    main()
