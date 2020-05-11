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
    argparser = configure_argparser()
    args = argparser.parse_args()
    category_url = 'http://tululu.org/l55/'
    json_path = choose_json_path(args.json_path, args.dest_folder)
    parse_category(category_url, args.start_page, args.end_page, args.dest_folder, json_path, args.skip_imgs, args.skip_txt)

def parse_category(category_url, start_page, end_page, dest_folder, json_path, skip_imgs, skip_txt):
    book_urls = get_category_book_urls(category_url, args.start_page, args.end_page)
    book_descriptions = download_books(book_urls, args.dest_folder, args.skip_imgs, args.skip_txt)
    save_json(book_descriptions, 'book_descriptions', json_path)

def configure_argparser():
    parser = argparse.ArgumentParser(
        description='Программа скачает книги с сайта tululu.org'
    )
    parser.add_argument('-s', '--start_page', type=int, default=1, help='Номер первой страницы скачивания')
    parser.add_argument('-e', '--end_page', type=int, default=9999, help='Номер страницы, до которой будут скачаны книги')
    parser.add_argument('-d', '--dest_folder', default='.', help='Путь к каталогу с результатами парсинга: картинкам, книгами, json')
    parser.add_argument('-i', '--skip_imgs', action='store_true', help='Не скачивать обложки книг')
    parser.add_argument('-t', '--skip_txt', action='store_true', help='Не скачивать текст книг')
    parser.add_argument('-j', '--json_path', default='.', help='Указать свой путь к *.json файлу с результатами')
    return parser

def choose_json_path(json_path, dest_folder):
    if json_path == '.' and dest_folder != '.':
        return dest_folder
    os.makedirs(json_path, exist_ok=True)
    return json_path

def download_books(book_urls, dest_folder, skip_imgs, skip_txt):
    os.makedirs(dest_folder, exist_ok=True)
    book_descriptions = []
    for url in book_urls:
        try:
            book_descriptions.append(download_book(url, dest_folder, skip_imgs, skip_txt))
        except HTTPError as err:
            category_logger.warning(err)
            continue
        except ConnectionError:
            sleep_time = 10
            category_logger.warning(f'Connection error. Start sleeping for {sleep_time} secs')
            sleep(sleep_time)
            continue
    category_logger.debug('Books were saved')
    return book_descriptions

def get_category_book_urls(category_url, start_page, end_page):
    book_urls = []
    for page in range(start_page, end_page):
        page_url = f'{category_url}/{page}/'
        try:
            urls = get_page_book_urls(page_url)
        except HTTPError:
            # tululu.org throw redirect when page number out of page amount
            break
        except ConnectionError:
            sleep_time = 10
            category_logger.warning(f'Connection error. Start sleeping for {sleep_time} secs')
            sleep(sleep_time)
            continue
        book_urls.extend(urls)
    category_logger.debug(f'Got {len(book_urls)} book urls')
    return book_urls
    
def get_page_book_urls(page_url):
    response = tululu.get_response(url)
    webpage = BeautifulSoup(response.text, 'lxml')
    book_tags = webpage.select('.ow_px_td .d_book')
    book_urls = [urljoin(page_url, book_tag.select_one('a')['href']) for book_tag in book_tags]
    category_logger.debug(f'Got urls form page "{page_url}"')
    return book_urls

def download_book(book_url, dest_folder, skip_imgs, skip_txt):
    book_path = None
    image_path = None
    book_id = book_url.split('/')[-2][1:]
    response = tululu.get_response(url)
    book_webpage = BeautifulSoup(response.text, 'lxml')
    title, author = tululu.get_book_title_and_author(book_webpage)
    if not skip_txt:
        book_path = tululu.download_book_text(book_id, title, dest_folder)
    if not skip_imgs:
        image_path = tululu.download_book_image(book_url, book_webpage, dest_folder)
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
    category_logger.debug(f'Book with id "{book_id}" was downloaded')
    return book_description

def save_json(info, filename, folder='.'):
    filename = f'{filename}.json'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(info, file, ensure_ascii=False)
    category_logger.debug(f'Json saved to {filename}')
    return filename


if __name__ == '__main__':
    main()
