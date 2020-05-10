import os
import json
import tululu
import logging
import argparse
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests import HTTPError, ConnectionError


category_logger = logging.getLogger('category_logger')


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # level='DEBUG',
    )
    args = parse_args()
    category_url = 'http://tululu.org/l55/'
    parse_category(category_url, args)

def parse_category(category_url, args):
    skip_txt = args.skip_txt
    skip_imgs = args.skip_imgs
    json_path = get_json_path(args)
    dest_folder = get_dest_folder(args)
    start_page, end_page = handle_page_args(args.start_page, args.end_page)
    category_logger.debug('All arguments were parsed and handled')
    download_category_books(category_url, start_page, end_page, json_path, dest_folder, skip_txt, skip_imgs)

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

def get_json_path(args):
    if args.json_path:
        os.makedirs(args.json_path, exist_ok=True)
        return args.json_path
    elif args.dest_folder:
        return args.dest_folder
    return ''

def get_dest_folder(args):
    if args.dest_folder:
        os.makedirs(args.dest_folder, exist_ok=True)
        return args.dest_folder
    return ''

def handle_page_args(start_page, end_page):
    if not start_page:
        start_page = 1
    if not end_page:
        end_page = 9999
    return start_page, end_page

def download_category_books(category_url, start_page, end_page, json_path, dest_folder, skip_imgs, skip_txt):
    book_urls = get_category_book_urls(category_url, start_page, end_page)
    book_descriptions = []
    for url in book_urls:
        try:
            book_descriptions.append(download_book(url, dest_folder, skip_imgs, skip_txt))
        except HTTPError:
            continue
        except ConnectionError:
            category_logger.debug('Start sleeping')
            sleep(10)
            continue
    save_json(book_descriptions, 'book_descriptions', json_path)
    category_logger.debug('Books were saved')

def get_category_book_urls(category_url, start_page, end_page):
    book_urls = []
    for page in range(start_page, end_page):
        page_url = f'{category_url}/{page}/'
        try:
            urls = get_page_book_urls(page_url)
        except HTTPError:
            break
        except ConnectionError:
            category_logger.debug('Start sleeping')
            sleep(10)
            continue
        book_urls.extend(urls)
    category_logger.debug(f'Got {len(book_urls)} book urls')
    return book_urls
    
def get_page_book_urls(page_url):
    webpage = parse_webpage(page_url)
    book_tags = webpage.select('.ow_px_td .d_book')
    book_urls = [urljoin(page_url, book_tag.select_one('a')['href']) for book_tag in book_tags]
    category_logger.debug(f'Got urls form page "{page_url}"')
    return book_urls

def parse_webpage(url):
    response = tululu.get_response(url)
    return BeautifulSoup(response.text, 'lxml')

def download_book(book_url, dest_folder, skip_imgs, skip_txt):
    book_path = ''
    image_path = ''
    book_id = book_url.split('/')[-2][1:]
    book_webpage = parse_webpage(book_url)
    title, author = tululu.get_book_title_and_author(book_webpage)
    if not skip_txt:
        book_path = tululu.download_book_text(book_id, title, dest_folder)
    if not skip_imgs:
        image_path = tululu.download_book_image(book_url, book_webpage, dest_folder)
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

def save_json(info, filename, folder=''):
    filename = f'{filename}.json'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(info, file, ensure_ascii=False)
    category_logger.debug(f'Json saved to {filename}')
    return filename


if __name__ == '__main__':
    main()
